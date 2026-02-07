import streamlit as st
import requests
from streamlit_cookies_manager import CookieManager

API_BASE = "http://127.0.0.1:8000"

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Login", layout="centered")


# ================= COOKIE MANAGER =================
cookies = CookieManager()

# ================= AUTO LOGIN (SAFE) =================
if cookies.ready():
    if not st.session_state.get("just_logged_out"):
        token = cookies.get("token")
        if token:
            st.session_state.token = token
            st.switch_page("pages/ai.py")
            st.stop()
if st.session_state.get("login_required"):
    st.warning("🔐 Please login to continue")
    st.session_state.pop("login_required")
# ================= HIDE SIDEBAR =================
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN UI =================
st.title("🔐 Login with OTP")
st.caption("Chat Bot • FastAPI • JWT")

email = st.text_input("Enter your email")

if st.button("Send OTP"):
    res = requests.post(f"{API_BASE}/otp", json={"email": email})
    if res.status_code == 200:
        st.session_state.email = email
        st.success("OTP sent successfully")
    else:
        st.error("Failed to send OTP")

if "email" in st.session_state:
    otp = st.text_input("Enter OTP")

    if st.button("Verify OTP"):
        res = requests.post(
            f"{API_BASE}/login",
            json={"email": st.session_state.email, "otp": otp}
        )

        if res.status_code == 200:
            data = res.json()

            # Save session
            st.session_state.token = data["access_token"]
            st.session_state.session_id=data['session_id']
            #print(f'{st.session_state.session_id} login ui')
            # Save cookie (PERSIST LOGIN)
            cookies["token"] = data["access_token"]
            cookies.save()
            st.switch_page("pages/ai.py")
            st.stop()
        else:
            st.error(res.json().get("detail", "Invalid OTP"))
