import streamlit as st
import requests
from streamlit_cookies_manager import CookieManager

API_BASE = "http://127.0.0.1:8000"

# ================= PAGE CONFIG =================
st.set_page_config(page_title="ChatBot", page_icon="🤖", layout="centered")

# ================= SESSION INIT =================
if "token" not in st.session_state:
    st.session_state.token = None

if "messages" not in st.session_state:
    st.session_state.messages = []

#print(f'{st.session_state} ai.py')
if "session_id" not in st.session_state:
    st.session_state.session_id = None
# ================= COOKIE MANAGER =================
cookies = CookieManager()

# ================= RESTORE TOKEN (SAFE) =================
if cookies.ready() and not st.session_state.token:
    cookie_token = cookies.get("token")
    if cookie_token:
        st.session_state.token = cookie_token

# ================= AUTH GUARD =================

if not st.session_state.token:
    st.session_state.login_required = True  # ✅ flag
    st.switch_page("pages/login.py")
    st.stop()
# ================= AUTH HEADER =================
headers = {
    "Authorization": f"Bearer {st.session_state.token}"
}

# ================= HIDE MULTIPAGE NAV =================
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ================= UI =================
st.title("🤖 AI ChatBot")
st.caption("FastAPI • RAG • JWT")

# ================= SIDEBAR =================
with st.sidebar:
    st.header("📎 Tools")

    mode = st.radio(
        "Select input type",
        ["💬 Domain Data", "📄 PDF", "🔗 Website"]
    )

    pdf_file = None
    website_url = None

    if mode == "📄 PDF":
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

    if mode == "🔗 Website":
        website_url = st.text_input("Website URL")

    # ================= LOGOUT (FINAL FIX) =================
    if st.button("Logout"):
        st.session_state.clear()
        st.session_state.just_logged_out = True 
        cookies["token"] = None
        cookies.save()
        st.rerun()
    if st.button("New Chat"):
        res=requests.post(f"{API_BASE}/new-session",headers=headers)
        #st.session_state.session_id=res["session_id"]
        #print(res.json()) 
        if res.status_code == 200:
            st.session_state.session_id =res.json()["session_id"]
            st.session_state.messages = []   # clear chat
            st.rerun() 
      
st.markdown("""
    <style>
    /* Reduce button height */
    div.stButton > button {
        height: 30px;
        padding: 2px 8px;
        font-size: 14px;
        margin: 0px;
    }

    /* Remove vertical gap between buttons */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0rem;
    }
    </style>
""", unsafe_allow_html=True)
with st.sidebar:
    history = requests.get(f"{API_BASE}/my-history", headers=headers)

    if history.status_code == 200:
        sessions = history.json()

        for chat in sessions:
            if chat["title"] != 'New Chat':
                if st.button(chat["title"], key=chat["session_uuid"]):
                    #if chat["title"] != "New Chat":
                        st.session_state.session_id = chat["session_uuid"]

                        res = requests.get(
                            f"{API_BASE}/chat-history/{chat['session_uuid']}",
                            headers=headers
                        )

                        if res.status_code == 200:
                            messages = res.json()

                            st.session_state.messages = [
                                {
                                    "role": "assistant" if m["sender"] == "bot" else "user",
                                    "content": m["message"]
                                }
                                for m in messages
                            ]

                            st.rerun()

          
# ================= CHAT HISTORY =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================= CHAT INPUT =================
user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    try:
        if mode == "💬 Domain Data":
            res = requests.post(
                f"{API_BASE}/chat",
                json={"message": user_input,'session_id': st.session_state.session_id},
                headers=headers
            )

        elif mode == "📄 PDF":
            if not pdf_file:
                st.warning("Upload a PDF first")
                st.stop()

            res = requests.post(
                f"{API_BASE}/pdf-chat",
                files={"file": pdf_file},
                data={"question": user_input,"session_id": st.session_state.session_id},
                headers=headers
            )

        elif mode == "🔗 Website":
            if not website_url:
                st.warning("Enter a website URL")
                st.stop()

            res = requests.post(
                f"{API_BASE}/url-chat",
                json={"url": website_url, "question": user_input,'session_id': st.session_state.session_id},
                headers=headers
            )

        # ================= TOKEN EXPIRED =================
        if res.status_code == 401:
            st.error("Session expired. Please login again.")

            st.session_state.clear()
            cookies["token"] = None
            cookies.save()

            st.switch_page("pages/login.py")
            st.stop()

        reply = res.json().get("reply", "No response")

    except Exception:
        reply = "❌ Server error"

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    st.rerun()
