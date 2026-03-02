import streamlit as st
import subprocess
import sys
import os

st.set_page_config(page_title="Gesture Balloon Pop 🎈", layout="centered")

st.title("🎈 Gesture Balloon Pop Game")
st.subheader("Human–Computer Interaction Demo")

st.markdown("""
### 🕹️ How to Play
- 🖐️ Open palm → Spawn balloon  
- ✊ Fist → Grab balloon  
- ✊ Touch balloon → Pop  
- ✋✋ Two open palms → Restart  
- ⏱️ 30 second challenge mode  
- ⎋ ESC → End game  
""")

status_placeholder = st.empty()
game_process = None

if "game_running" not in st.session_state:
    st.session_state.game_running = False

if st.button("▶️ Start Game") and not st.session_state.game_running:
    st.success("Launching game...")
    with open("game_status.txt", "w") as f:
        f.write("RUNNING")

    game_process = subprocess.Popen([sys.executable, "main.py"])
    st.session_state.game_running = True

# ----------------- STATUS MONITOR -----------------

if st.session_state.game_running:
    status_placeholder.info("🎮 Game is running... Press ESC to stop.")

    if os.path.exists("game_status.txt"):
        with open("game_status.txt", "r") as f:
            status = f.read().strip()

        if status == "ENDED":
            status_placeholder.success("✅ Game Ended 🎉 Thanks for playing!")
            st.session_state.game_running = False

else:
    status_placeholder.warning("🕹️ Game not running.")

st.markdown("---")
st.caption("Built with MediaPipe + OpenCV + Streamlit")
