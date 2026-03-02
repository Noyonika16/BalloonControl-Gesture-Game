import cv2
import mediapipe as mp
import numpy as np
import time
import random
import pygame
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ----------------- STREAMLIT STATUS FLAG -----------------
with open("game_status.txt", "w") as f:
    f.write("RUNNING")

# ----------------- INIT SOUND -----------------
pygame.mixer.init()
pop_sound = pygame.mixer.Sound("pop.mp3")  # or "pop.wav"

# ----------------- GESTURE FUNCTIONS -----------------

def is_fist(lm):
    return (lm[8][1] > lm[6][1] and
            lm[12][1] > lm[10][1] and
            lm[16][1] > lm[14][1] and
            lm[20][1] > lm[18][1])

def is_open_palm(lm):
    return (lm[8][1] < lm[6][1] and
            lm[12][1] < lm[10][1] and
            lm[16][1] < lm[14][1] and
            lm[20][1] < lm[18][1])

# ----------------- CALLBACK -----------------

latest_result = None
def result_callback(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

# ----------------- MEDIAPIPE -----------------

base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=result_callback
)
detector = vision.HandLandmarker.create_from_options(options)

# ----------------- GAME STATE -----------------

obj_x, obj_y = 0, 0
obj_radius = 40
grab_radius = obj_radius + 120
pop_radius = obj_radius + 15

obj_grabbed = False
object_visible = False
object_spawned = False

alpha = 0.25
grab_offset_x = 0
grab_offset_y = 0

balloon_color = (0, 0, 255)

score = 0
score_scale = 1.0
score_flash_time = 0

last_hand_x, last_hand_y = None, None
last_seen_time = 0
HAND_TIMEOUT = 0.4
restart_counter = 0

# ----------------- TIMER MODE -----------------

GAME_DURATION = 30
game_start_time = time.time()
game_over = False

# ----------------- AUTO RESPAWN -----------------

respawn_time = None
RESPAWN_DELAY = 0.7

# ----------------- PARTICLES -----------------

particles = []

# ----------------- HELPERS -----------------

def random_color():
    return (random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255))

def spawn_particles(x, y):
    for _ in range(25):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-5, 5),
            "vy": random.uniform(-5, 5),
            "life": random.randint(15, 30)
        })

# ----------------- MAIN LOOP -----------------

cap = cv2.VideoCapture(0)
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    timestamp_ms = int((time.time() - start_time) * 1000)
    detector.detect_async(mp_image, timestamp_ms)

    hand_x, hand_y = None, None
    gesture = "No Hand"
    num_hands = 0
    lm_list = []

    # ----------------- READ HANDS -----------------
    if latest_result and latest_result.hand_landmarks:
        num_hands = len(latest_result.hand_landmarks)

        # ---- Restart gesture: two open palms (stable) ----
        if num_hands == 2:
            lm1 = [(lm.x, lm.y) for lm in latest_result.hand_landmarks[0]]
            lm2 = [(lm.x, lm.y) for lm in latest_result.hand_landmarks[1]]

            if is_open_palm(lm1) and is_open_palm(lm2):
                restart_counter += 1
            else:
                restart_counter = 0

            if restart_counter >= 3:
                score = 0
                game_start_time = time.time()
                game_over = False
                object_visible = False
                object_spawned = False
                obj_grabbed = False
                particles.clear()
                respawn_time = None
                restart_counter = 0
                print("🔄 GAME RESET")
        else:
            restart_counter = 0

        # ---- Use first hand for interaction ----
        hand_landmarks = latest_result.hand_landmarks[0]

        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append((lm.x, lm.y))
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        if len(lm_list) == 21:
            if is_fist(lm_list):
                gesture = "FIST"
            elif is_open_palm(lm_list):
                gesture = "OPEN_PALM"
            else:
                gesture = "OTHER"

            hand_x = int(lm_list[8][0] * w)
            hand_y = int(lm_list[8][1] * h)

            last_hand_x, last_hand_y = hand_x, hand_y
            last_seen_time = time.time()

    else:
        # ---- HAND LOST FALLBACK ----
        if last_hand_x is not None and (time.time() - last_seen_time) < HAND_TIMEOUT:
            hand_x, hand_y = last_hand_x, last_hand_y
        else:
            hand_x, hand_y = None, None
            obj_grabbed = False

    # ----------------- TIMER -----------------
    elapsed = time.time() - game_start_time
    time_left = max(0, int(GAME_DURATION - elapsed))
    if time_left <= 0:
        game_over = True

    # ----------------- MANUAL FIRST SPAWN -----------------
    if (not game_over and not object_visible and not object_spawned
        and respawn_time is None and gesture == "OPEN_PALM" and len(lm_list) == 21):

        obj_x = int(lm_list[8][0] * w)
        obj_y = int(lm_list[8][1] * h)
        object_visible = True
        object_spawned = True
        balloon_color = random_color()
        print("🟢 OBJECT SPAWNED (manual)")

    # ----------------- AUTO RESPAWN -----------------
    if (not game_over and not object_visible and respawn_time is not None
        and time.time() - respawn_time > RESPAWN_DELAY):

        obj_x = random.randint(80, w - 80)
        obj_y = random.randint(80, h - 80)
        object_visible = True
        object_spawned = True
        balloon_color = random_color()
        respawn_time = None
        print("🟢 AUTO RESPAWNED")

    # ----------------- INTERACTION -----------------
    if not game_over and hand_x is not None and hand_y is not None and object_visible:

        dist_to_obj = np.hypot(hand_x - obj_x, hand_y - obj_y)

        # ---- Grab ----
        if gesture == "FIST" and dist_to_obj < grab_radius and not obj_grabbed:
            obj_grabbed = True
            grab_offset_x = obj_x - hand_x
            grab_offset_y = obj_y - hand_y

        if gesture != "FIST" and obj_grabbed:
            obj_grabbed = False

        # ---- Move ----
        if obj_grabbed:
            target_x = hand_x + grab_offset_x
            target_y = hand_y + grab_offset_y
            obj_x = int(alpha * target_x + (1 - alpha) * obj_x)
            obj_y = int(alpha * target_y + (1 - alpha) * obj_y)

        # ---- Pop ----
        if obj_grabbed and dist_to_obj < pop_radius:
            score += 1
            pop_sound.play()
            score_flash_time = time.time()
            score_scale = 1.8

            spawn_particles(obj_x, obj_y)

            object_visible = False
            object_spawned = False
            obj_grabbed = False
            respawn_time = time.time()

            print("🎈 POP! Score =", score)

    # ----------------- DRAW BALLOON -----------------
    if object_visible:
        color = (0, 255, 0) if obj_grabbed else balloon_color
        cv2.circle(frame, (obj_x, obj_y), obj_radius, color, -1)

    # ----------------- PARTICLES -----------------
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        cv2.circle(frame, (int(p["x"]), int(p["y"])), 4, (255, 255, 255), -1)
        if p["life"] <= 0:
            particles.remove(p)

    # ----------------- SCORE ANIMATION -----------------
    if time.time() - score_flash_time < 0.3:
        score_scale = max(1.0, score_scale - 0.08)
    else:
        score_scale = 1.0

    # ----------------- UI -----------------
    pretty_gesture = gesture
    if gesture == "OPEN_PALM":
        pretty_gesture = "OPEN PALM 🖐️"
    elif gesture == "FIST":
        pretty_gesture = "FIST ✊"

    cv2.putText(frame, f"Gesture: {pretty_gesture}",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 0, 0), 2)

    font_scale = 1.2 * score_scale
    cv2.putText(frame, f"Score: {score}",
                (10, 90), cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, (0, 220, 0), 3)

    cv2.putText(frame, f"Time Left: {time_left}s",
                (10, 140), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 200, 255), 2)

    if game_over:
        cv2.putText(frame, "GAME OVER",
                    (w//2 - 180, h//2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2, (0, 0, 255), 4)

        cv2.putText(frame, "Show two open palms to restart",
                    (w//2 - 280, h//2 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2)

    cv2.imshow("Gesture Balloon Pop Game", frame)

    # ----------------- ESC EXIT -----------------
    if cv2.waitKey(1) & 0xFF == 27:
        with open("game_status.txt", "w") as f:
            f.write("ENDED")
        break

cap.release()
cv2.destroyAllWindows()

# ----------------- SAFE EXIT FLAG -----------------
with open("game_status.txt", "w") as f:
    f.write("ENDED")
