from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import auth, websocket
from app.websocket import ACTIVE_CONNECTIONS, ACTIVE_GEMINI_SESSIONS

# FastAPI Setup
app = FastAPI(title="Edza AI Voice Service")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# Mount the routers from other modules
app.include_router(auth.router)
app.include_router(websocket.router)

@app.get("/status")
async def get_status():
    """An HTTP endpoint to get real-time stats about the service."""
    return {
        "active_connections": len(ACTIVE_CONNECTIONS),
        "active_gemini_sessions": len(ACTIVE_GEMINI_SESSIONS)
    }
