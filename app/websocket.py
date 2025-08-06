import os, asyncio, logging, json, wave, base64, uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.auth import get_current_user, User
from app.config import settings
from app.services.gcs_utils import upload_to_gcs
from google import genai
from google.genai import types


router = APIRouter()

logging.basicConfig(level=logging.INFO, format='%(message)s')

# A thread-safe set to store IDs of all active WebSocket connections
ACTIVE_CONNECTIONS = set()
# A thread-safe set to store IDs of only the sessions actively using the Gemini API
ACTIVE_GEMINI_SESSIONS = set()


MODEL = settings.GEMINI_MODEL
RECORDINGS_DIR = settings.RECORDINGS_DIR
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())


@router.websocket("/ws-ai")
async def websocket_endpoint(websocket: WebSocket, current_user: User = Depends(get_current_user)):

    connection_id = str(uuid.uuid4())
    ACTIVE_CONNECTIONS.add(connection_id)

    # Create a context dictionary that will be part of every log message
    log_context = {"connection_id": connection_id, "user_id": current_user.username}

    await websocket.accept()
    logging.info(json.dumps({**log_context, "event": "connection_accepted", "total_active_connections": len(ACTIVE_CONNECTIONS)}))

    try:
        session_id = None
        while True:
            try:
                # This prevents a crash if binary data is received unexpectedly.
                message = await websocket.receive()
                if "text" in message:
                    message_json = json.loads(message["text"])
                    if message_json.get("type") == "start_call":
                        session_id = f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
                        log_context["session_id"] = session_id # Add it to our logging context
                        logging.info(json.dumps({**log_context, "event": "start_call_signal_received"}))
                        break
                    else:
                        logging.warning(json.dumps({**log_context, "event": "unexpected_idle_message", "message": message_json}))
                elif "bytes" in message:
                    logging.warning(json.dumps({**log_context, "event": "unexpected_idle_binary_data"}))

                    
            except WebSocketDisconnect:
                logging.info(json.dumps({**log_context, "event": "client_disconnected_during_idle"}))
                return # Exit the endpoint
            except Exception as e:
                logging.error(json.dumps({**log_context, "event": "error_in_idle_loop", "error": str(e)}), exc_info=True)
                return
        

        # new gemini session creates here
        ACTIVE_GEMINI_SESSIONS.add(session_id)
        logging.info(json.dumps({**log_context, "event": "gemini_session_initializing", "total_active_gemini_sessions": len(ACTIVE_GEMINI_SESSIONS)}))

        # Check if the GCS bucket is configured before proceeding
        if settings.GCS_BUCKET_NAME:
             # Create a unique folder for each call session inside the bucket
            blob_folder = f"calls/{datetime.now().strftime('%Y/%m/%d')}/{session_id}/"
        else:
            blob_folder = None

        # These paths point to the temporary disk on the Render server
        user_wav_path = os.path.join(RECORDINGS_DIR, f"{session_id}_user.wav")
        gemini_wav_path = os.path.join(RECORDINGS_DIR, f"{session_id}_gemini.wav")

        user_wav_writer = wave.open(user_wav_path, 'wb')
        user_wav_writer.setnchannels(1); user_wav_writer.setsampwidth(2); user_wav_writer.setframerate(16000)

        gemini_wav_writer = wave.open(gemini_wav_path, 'wb')
        gemini_wav_writer.setnchannels(1); gemini_wav_writer.setsampwidth(2); gemini_wav_writer.setframerate(24000)

        #  Configure the session for both audio and vision from the start 
        live_config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(language_code=settings.LANGUAGE_CODE),
            output_audio_transcription={},
            system_instruction=settings.SYSTEM_PROMPT,
            realtime_input_config=types.RealtimeInputConfig(
                automatic_activity_detection=types.AutomaticActivityDetection(
                    silence_duration_ms=1000,
                    prefix_padding_ms=100,
                )
            ),
        )

        try:
            async with client.aio.live.connect(model=MODEL, config=live_config) as session:
                logging.info(json.dumps({**log_context, "event": "gemini_session_started_successfully", "model": MODEL}))

                await websocket.send_json({"type": "call_started"})

                # This task now correctly handles both audio and video frames
                async def handle_user_input_task(log_ctx):
                    try:
                        while True:
                            message = await websocket.receive()
                            # binary audio data
                            if "bytes" in message:
                                data = message["bytes"]
                                user_wav_writer.writeframes(data)
                                logging.info(json.dumps({**log_ctx, "event": "audio_chunk_received", "size_bytes": len(data)}))
                                # Before sending to Gemini, we must encode the raw bytes into a Base64 string.
                                encoded_audio = base64.b64encode(data).decode('utf-8')
                                await session.send(input={"data": encoded_audio, "mime_type": "audio/pcm;rate=16000"})

                            elif "text" in message:
                                control_msg = json.loads(message["text"])
                                msg_type = control_msg.get("type")

                                if msg_type == "video_frame":
                                    #  This is for VIDEO, which arrives as a Base64 string 
                                    # We just need to forward the string directly. DO NOT decode it.
                                    img_payload = control_msg["payload"] 
                                    logging.info(json.dumps({**log_ctx, "event": "video_frame_received", "size_bytes": len(img_payload)}))
                                    # sending live frames 
                                    await session.send(input={"data": img_payload, "mime_type": "image/jpeg"})

                                elif msg_type == "audio_stream_end":
                                    logging.info(json.dumps({**log_ctx, "event": "audio_stream_end_signal_received"}))
                                    break
                    except WebSocketDisconnect:
                        logging.warning(json.dumps({**log_ctx, "event": "client_disconnected_during_call"}))

                        # it correctly handles audio and text responses
                async def receive_responses_task(log_ctx):
                    try:
                        while True:
                            full_gemini_transcript = ""
                            async for response in session.receive():
                                # Safely check if the 'user_utterance' attribute exists before accessing it.
                                if hasattr(response, 'user_utterance') and (ut := response.user_utterance) and (uat := ut.output_transcription) and uat.text:
                                    await websocket.send_json({"type": "user_transcript", "text": uat.text.strip()})

                                if response.data:
                                    gemini_wav_writer.writeframes(response.data)
                                    await websocket.send_bytes(response.data)
                                
                                if (sc := response.server_content) and (oat := sc.output_transcription) and oat.text:
                                    transcript_chunk = oat.text
                                    full_gemini_transcript += transcript_chunk
                                    await websocket.send_json({"type": "gemini_chunk", "text": transcript_chunk})
                            if full_gemini_transcript:
                                logging.info(json.dumps({**log_ctx, "event": "gemini_full_transcript_received", "transcript": full_gemini_transcript.strip()}))
                    except WebSocketDisconnect:
                        logging.warning(json.dumps({**log_ctx, "event": "client_disconnected_while_receiving_response"}))

                send_task = asyncio.create_task(handle_user_input_task(log_context))
                receive_task = asyncio.create_task(receive_responses_task(log_context))

                done, pending = await asyncio.wait([send_task, receive_task], return_when=asyncio.FIRST_COMPLETED)
                for task in pending: task.cancel()
                for task in done:
                    if task.exception(): raise task.exception()

        except Exception as e:
            logging.error(json.dumps({**log_context, "event": "gemini_session_error", "error": str(e)}), exc_info=True)
        finally:
            ACTIVE_GEMINI_SESSIONS.discard(session_id)
            logging.info(json.dumps({**log_context, "event": "gemini_session_ended", "total_active_gemini_sessions": len(ACTIVE_GEMINI_SESSIONS)}))
            logging.info(json.dumps({**log_context, "event": "file_processing_started"}))
            user_wav_writer.close()
            gemini_wav_writer.close()

            # UPLOAD AND CLEANUP LOGIC 
            if blob_folder:
                if upload_to_gcs(user_wav_path, f"{blob_folder}user.wav"):
                    os.remove(user_wav_path)
                if upload_to_gcs(gemini_wav_path, f"{blob_folder}gemini.wav"):
                    os.remove(gemini_wav_path)

            try:
                await websocket.send_json({"type": "call_ended"})
                logging.info(json.dumps({**log_context, "event": "call_ended_signal_sent"}))
            except (WebSocketDisconnect, RuntimeError):
                logging.warning(json.dumps({**log_context, "event": "client_disconnected_before_call_ended_signal"}))
                raise WebSocketDisconnect

    except WebSocketDisconnect:
        logging.info(json.dumps({**log_context, "event": "websocket_closed_by_client"}))
    except Exception as e:
        logging.error(json.dumps({**log_context, "event": "unhandled_endpoint_error", "error": str(e)}), exc_info=True)
    finally:
        ACTIVE_CONNECTIONS.discard(connection_id)
        logging.info(json.dumps({
        **log_context, 
        "event": "connection_closed",
        "total_active_connections": len(ACTIVE_CONNECTIONS) # Now we log the NEW total
    }))