# import requests

# # Gemini API configuration
# GEMINI_API_KEY = "AIzaSyAufdd2Tsje03N9Ki3RHDpGKxB_RpOoCUc"
# GEMINI_ENDPOINT = (
#     f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
# )

# def ask_gemini(prompt: str) -> str:
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     data = {
#         "contents": [
#             {
#                 "parts": [
#                     {"text": prompt}
#                 ]
#             }
#         ]
#     }

#     response = requests.post(
#         GEMINI_ENDPOINT,
#         params={"key": GEMINI_API_KEY},
#         headers=headers,
#         json=data
#     )

#     if response.status_code == 200:
#         try:
#             return response.json()['candidates'][0]['content']['parts'][0]['text']
#         except (KeyError, IndexError) as e:
#             return f"Unexpected response format: {response.json()}"
#     else:
#         return f"Error {response.status_code}: {response.text}"
# import os
# import requests
# from dotenv import load_dotenv

# # Load API key from .env
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# GEMINI_ENDPOINT = (
#     "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
# )

# def ask_gemini(prompt: str) -> str:
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     data = {
#         "contents": [
#             {
#                 "parts": [
#                     {"text": prompt}
#                 ]
#             }
#         ]
#     }

#     response = requests.post(
#         GEMINI_ENDPOINT,
#         params={"key": GEMINI_API_KEY},
#         headers=headers,
#         json=data
#     )

#     if response.status_code == 200:
#         try:
#             return response.json()['candidates'][0]['content']['parts'][0]['text']
#         except (KeyError, IndexError) as e:
#             return f"Unexpected response format: {response.json()}"
#     else:
#         return f"Error {response.status_code}: {response.text}"
import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# === Setup Logging ===
log_dir = os.path.dirname(os.path.abspath(__file__))  # current dir
log_file_path = os.path.join(log_dir, "gemini_errors.log")

logging.basicConfig(
    filename=log_file_path,
    level=logging.ERROR,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === Load Environment Variables ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
)

# === Gemini Request Function ===
def ask_gemini(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(
            GEMINI_ENDPOINT,
            params={"key": GEMINI_API_KEY},
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            try:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError) as e:
                logging.error(f"Unexpected response format: {response.json()}")
                return f"Unexpected response format: {response.json()}"
        else:
            logging.error(f"Error {response.status_code}: {response.text}")
            return f"Error {response.status_code}: {response.text}"

    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return f"Exception occurred: {str(e)}"
