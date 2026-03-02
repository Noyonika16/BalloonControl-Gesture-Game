🎈 Gesture Balloon Pop – AI Powered Hand Gesture Game

Turn your webcam into a controller.

This is a real-time gesture-controlled game where you pop balloons using only your hand — no mouse, no keyboard.

Built using MediaPipe + OpenCV + Streamlit + Pygame, this project explores real-time Computer Vision, gesture recognition, and Human–Computer Interaction.

🚀 Demo Concept

🖐️ Open Palm → Spawn Balloon

✊ Fist → Grab Balloon

🎈 Touch → Pop

✋✋ Two Open Palms → Restart

⏱️ 30-Second Challenge Mode

⎋ ESC → Exit

🧠 Why I Built This

This started as a “build something fun” experiment.

It quickly became a deep dive into:

+Real-time hand landmark detection

+Gesture classification logic

+Async detection pipelines

+Frame timing & smoothing

+Game state management

+Sound feedback systems

+UI integration with Streamlit

+Designing intuitive human-computer interaction

This project helped me move from:

Learning AI concepts → Engineering interactive AI systems

🏗️ Tech Stack

Python

MediaPipe (Hand Landmarker – Live Stream Mode)

OpenCV

NumPy

Pygame (Sound Effects)

Streamlit (Launcher UI)

⚙️ How It Works
1️⃣ Hand Tracking

MediaPipe detects 21 hand landmarks in real time.

2️⃣ Gesture Recognition

Simple but effective rule-based detection:

Fist → All fingertips below knuckles

Open Palm → All fingertips above knuckles

3️⃣ Object Interaction Logic

Grab radius detection

Smooth interpolation (alpha blending)

Pop radius trigger

Particle burst animation

Score scaling animation

4️⃣ Game Flow

30-second timer

Auto-respawn system

Restart gesture detection (two open palms)

Hand-loss fallback mechanism

📂 Project Structure
📦 gesture-balloon-pop
 ┣ 📜 main.py            # Core game logic
 ┣ 📜 app.py             # Streamlit launcher
 ┣ 📜 hand_landmarker.task
 ┣ 📜 pop.mp3
 ┣ 📜 game_status.txt
 ┗ 📜 README.md
▶️ Installation
1️⃣ Clone the Repository
git clone https://github.com/yourusername/gesture-balloon-pop.git
cd gesture-balloon-pop
2️⃣ Install Dependencies
pip install -r requirements.txt

Or manually:

pip install opencv-python mediapipe numpy pygame streamlit
3️⃣ Run the Game

Option 1 — Direct:

python main.py

Option 2 — Streamlit UI:

streamlit run app.py
🎯 What Makes This Interesting

Real-time AI interaction

Gesture-based control system

Lightweight but complete game loop

Clean separation of detection + interaction + UI

Beginner-friendly but system-level learning experience

📈 Future Improvements:

Add more gestures (swipe, pinch)

Add difficulty levels

Add leaderboard system

Convert to web deployment

Integrate ML-based gesture classifier instead of rule-based logic

Add multi-player mode


Small interactive projects teach more than passive tutorials.

Real-time systems force you to think about:

Latency

Stability

Edge cases

User experience

System integration

This project helped me deeply understand how Computer Vision connects to real-world interaction.

👨‍💻 Author

Noyonika Mukherjee
