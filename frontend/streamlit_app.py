# import sys
# import os
# import streamlit as st
# import requests

# # Add parent directory to sys.path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
# sys.path.insert(0, parent_dir)

# from utils.gemini_api import ask_gemini

# API_URL = "https://localhost:8000"

# # Initialize session state
# if 'token' not in st.session_state:
#     st.session_state.token = None
# if 'authenticated' not in st.session_state:
#     st.session_state.authenticated = False
# if 'show_login' not in st.session_state:
#     st.session_state.show_login = False
# if 'username' not in st.session_state:
#     st.session_state.username = None
# if 'all_chat_histories' not in st.session_state:
#     st.session_state.all_chat_histories = {}  

# # Sidebar
# st.sidebar.title("🔐 Secure Gemini Chat")

# # Login toggle
# if not st.session_state.authenticated:
#     if st.sidebar.button("Login"):
#         st.session_state.show_login = not st.session_state.show_login
# else:
#     if st.sidebar.button("Logout"):
#         st.session_state.token = None
#         st.session_state.authenticated = False
#         st.session_state.username = None
#         st.sidebar.success("🔒 Logged out successfully")

# # Login form
# if st.session_state.show_login and not st.session_state.authenticated:
#     with st.sidebar.form("login_form"):
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("OK")

#         if submitted:
#             try:
#                 response = requests.post(
#                     f"{API_URL}/token",
#                     data={"username": username, "password": password},
#                     verify=False
#                 )
#                 if response.status_code == 200:
#                     st.session_state.token = response.json()["access_token"]
#                     st.session_state.authenticated = True
#                     st.session_state.username = username
#                     st.session_state.show_login = False

#                     # Create history entry for new user
#                     if username not in st.session_state.all_chat_histories:
#                         st.session_state.all_chat_histories[username] = []

#                     st.sidebar.success(f"✅ Logged in as {username}")
#                 else:
#                     st.sidebar.error("❌ Invalid credentials")
#             except Exception as e:
#                 st.sidebar.error(f"Connection Error: {e}")

# # Title
# st.title("🧠 Edza AI Chatbot")

# # Chat input
# query = st.text_input("Ask something:", placeholder="Type your query and press Enter...", key="chat_input")

# if st.button("Enter"):
#     if query.strip():
#         if st.session_state.authenticated and st.session_state.username:
#             with st.spinner("Thinking..."):
#                 response = ask_gemini(query)
#             st.success("Gemini says:")
#             st.write(response)
#             title = query[:40] + ("..." if len(query) > 40 else "")
#             st.session_state.all_chat_histories[st.session_state.username].append({
#                 "title": title,
#                 "query": query,
#                 "response": response
#             })
#         else:
#             st.warning("Not Authenticated, Please Authenticate first.")

# if st.session_state.authenticated and st.session_state.username:
#     chat_history = st.session_state.all_chat_histories.get(st.session_state.username, [])
#     if chat_history:
#         st.sidebar.markdown(f"### Chat History ({st.session_state.username})")
#         for i, entry in enumerate(reversed(chat_history), 1):
#             st.sidebar.markdown(f"- {entry['title']}")

import sys
import os
import streamlit as st
import requests
import json

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

from utils.gemini_api import ask_gemini

API_URL = "http://localhost:8000"
CHAT_DATA_DIR = os.path.join(parent_dir, "chat_data")
os.makedirs(CHAT_DATA_DIR, exist_ok=True)

# ------------------ Chat History Persistence ------------------ #
def get_history_path(username):
    return os.path.join(CHAT_DATA_DIR, f"{username}.json")

def load_chat(username):
    path = get_history_path(username)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_chat(username, history):
    path = get_history_path(username)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

# ------------------ Streamlit State Setup ------------------ #
if 'token' not in st.session_state:
    st.session_state.token = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ------------------ Sidebar: Login/Logout ------------------ #
st.sidebar.title("🔐 Secure Gemini Chat")

if not st.session_state.authenticated:
    if st.sidebar.button("Login"):
        st.session_state.show_login = not st.session_state.show_login
else:
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.chat_history = []
        st.sidebar.success("🔒 Logged out successfully")

# ------------------ Login Form ------------------ #
if st.session_state.show_login and not st.session_state.authenticated:
    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("OK")

        if submitted:
            try:
                response = requests.post(
                    f"{API_URL}/token",
                    data={"username": username, "password": password},
                    # verify=False
                )
                if response.status_code == 200:
                    st.session_state.token = response.json()["access_token"]
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.show_login = False

                    # Load previous history
                    st.session_state.chat_history = load_chat(username)
                    st.sidebar.success(f"✅ Logged in as {username}")
                else:
                    st.sidebar.error("❌ Invalid credentials")
            except Exception as e:
                st.sidebar.error(f"Connection Error: {e}")

# ------------------ Main Chat UI ------------------ #
st.title("🧠 Edza AI Chatbot")

query = st.text_input("Ask something:", placeholder="Type your query and press Enter...", key="chat_input")

if st.button("Enter"):
    if query.strip():
        if st.session_state.authenticated and st.session_state.username:
            with st.spinner("Thinking..."):
                response = ask_gemini(query)

            st.success("Gemini says:")
            st.write(response)

            title = query[:40] + ("..." if len(query) > 40 else "")
            new_entry = {
                "title": title,
                "query": query,
                "response": response
            }

            st.session_state.chat_history.append(new_entry)
            save_chat(st.session_state.username, st.session_state.chat_history)

        else:
            st.warning("Not Authenticated, Please Authenticate first.")

# ------------------ Sidebar History ------------------ #
if st.session_state.authenticated and st.session_state.username:
    if st.session_state.chat_history:
        st.sidebar.markdown(f"### Chat History ({st.session_state.username})")
        for entry in reversed(st.session_state.chat_history):
            st.sidebar.markdown(f"- {entry['title']}")


# import sys
# import os
# import streamlit as st
# import requests
# import json

# # Add parent directory to sys.path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
# sys.path.insert(0, parent_dir)

# API_URL = "https://localhost:8000"  # Your FastAPI backend URL
# CHAT_DATA_DIR = os.path.join(parent_dir, "chat_data")
# os.makedirs(CHAT_DATA_DIR, exist_ok=True)

# # ------------------ Chat History Persistence ------------------ #
# def get_history_path(username):
#     return os.path.join(CHAT_DATA_DIR, f"{username}.json")

# def load_chat(username):
#     path = get_history_path(username)
#     if os.path.exists(path) and os.path.getsize(path) > 0:
#         with open(path, "r") as f:
#             return json.load(f)
#     return []

# def save_chat(username, history):
#     path = get_history_path(username)
#     with open(path, "w") as f:
#         json.dump(history, f, indent=2)

# # ------------------ Secure Gemini Request via Backend ------------------ #
# def ask_gemini_backend(prompt):
#     try:
#         headers = {
#             "Authorization": f"Bearer {st.session_state.token}",
#             "Content-Type": "application/json"
#         }

#         response = requests.post(
#             f"{API_URL}/ask-gemini",
#             json={"prompt": prompt},
#             headers=headers,
#             verify=False
#         )
#         if response.status_code == 200:
#             return response.json()["response"]
#         else:
#             return f"❌ Error {response.status_code}: {response.text}"
#     except Exception as e:
#         return f"🚨 Connection error: {str(e)}"


# # ------------------ Streamlit Session State Setup ------------------ #
# if 'token' not in st.session_state:
#     st.session_state.token = None
# if 'authenticated' not in st.session_state:
#     st.session_state.authenticated = False
# if 'show_login' not in st.session_state:
#     st.session_state.show_login = False
# if 'username' not in st.session_state:
#     st.session_state.username = None
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []

# # ------------------ Sidebar: Login/Logout ------------------ #
# st.sidebar.title("🔐 Secure Gemini Chat")

# if not st.session_state.authenticated:
#     if st.sidebar.button("Login"):
#         st.session_state.show_login = not st.session_state.show_login
# else:
#     if st.sidebar.button("Logout"):
#         st.session_state.token = None
#         st.session_state.authenticated = False
#         st.session_state.username = None
#         st.session_state.chat_history = []
#         st.sidebar.success("🔒 Logged out successfully")

# # ------------------ Login Form ------------------ #
# if st.session_state.show_login and not st.session_state.authenticated:
#     with st.sidebar.form("login_form"):
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("OK")

#         if submitted:
#             try:
#                 response = requests.post(
#                     f"{API_URL}/token",
#                     data={"username": username, "password": password},
#                     verify=False
#                 )
#                 if response.status_code == 200:
#                     st.session_state.token = response.json()["access_token"]
#                     st.session_state.authenticated = True
#                     st.session_state.username = username
#                     st.session_state.show_login = False

#                     st.session_state.chat_history = load_chat(username)
#                     st.sidebar.success(f"✅ Logged in as {username}")
#                 else:
#                     st.sidebar.error("❌ Invalid credentials")
#             except Exception as e:
#                 st.sidebar.error(f"🚨 Server Error: {str(e)}")

# # ------------------ Main Chat UI ------------------ #
# st.title("🧠 Edza AI Chatbot")

# query = st.text_input(
#     "Ask something:",
#     placeholder="Type your query and press Enter...",
#     key="chat_input"
# )

# if st.button("Enter"):
#     if query.strip():
#         if st.session_state.authenticated and st.session_state.username:
#             with st.spinner("Thinking..."):
#                 response = ask_gemini_backend(query)

#             st.success("Gemini says:")
#             st.write(response)

#             title = query[:40] + ("..." if len(query) > 40 else "")
#             new_entry = {
#                 "title": title,
#                 "query": query,
#                 "response": response
#             }

#             st.session_state.chat_history.append(new_entry)
#             save_chat(st.session_state.username, st.session_state.chat_history)

#         else:
#             st.warning("🔐 Please log in to chat.")

# # ------------------ Sidebar Chat History ------------------ #
# if st.session_state.authenticated and st.session_state.username:
#     if st.session_state.chat_history:
#         st.sidebar.markdown(f"### 🕘 Chat History ({st.session_state.username})")
#         for entry in reversed(st.session_state.chat_history):
#             st.sidebar.markdown(f"- {entry['title']}")
