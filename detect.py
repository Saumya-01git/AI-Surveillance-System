import cv2
from ultralytics import YOLO
import time
import math
from db import insert_alert

# ---------------- AI MODEL ----------------
model = YOLO("yolov8n.pt")

# ---------------- BASE CONFIG ----------------
LOITER_TIME = 10
LOITER_MOVEMENT_TOLERANCE = 15
SPEED_THRESHOLD = 40
INTERACTION_DISTANCE = 60
INTERACTION_TIME = 2
CROWD_LIMIT = 8

RISK_THRESHOLD = 3
RISK_DECAY = 0.1

# Event cooldowns
LOITER_GAP = 8
SPEED_GAP = 5
INTERACTION_GAP = 6
CROWD_GAP = 10

# ---------------- NEW FEATURES ----------------
RESTRICTED_ZONE = (100, 100, 450, 400)  # x1,y1,x2,y2
RESTRICTED_WEIGHT = 5
WEAPON_BOOST = 10
# ------------------------------------------------


def run_detection(source, environment):

    # -------- ENVIRONMENT WEIGHTS --------
    if environment == "Railway Station":
        LOITER_WEIGHT = 1
        SPEED_WEIGHT = 1
        INTERACTION_WEIGHT = 1
        CROWD_WEIGHT = 2

    elif environment == "Shopping Mall":
        LOITER_WEIGHT = 2
        SPEED_WEIGHT = 2
        INTERACTION_WEIGHT = 3
        CROWD_WEIGHT = 1

    elif environment == "Airport":
        LOITER_WEIGHT = 4
        SPEED_WEIGHT = 1
        INTERACTION_WEIGHT = 1
        CROWD_WEIGHT = 2

    else:
        LOITER_WEIGHT = 2
        SPEED_WEIGHT = 2
        INTERACTION_WEIGHT = 2
        CROWD_WEIGHT = 2
    # -------------------------------------

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("Video not opening")
        return

    first_seen = {}
    prev_positions = {}
    interaction_start = {}
    risk_score = {}
    last_event_time = {}
    last_crowd_time = 0
    alerted_persons = set()
    alert_reasons = {}
    weapon_detected = False

    print(f"\nRunning in {environment} mode...\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, persist=True)
        current_time = time.time()

        person_count = 0
        current_positions = {}

        # Draw Restricted Zone
        zx1, zy1, zx2, zy2 = RESTRICTED_ZONE
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 0, 255), 2)
        cv2.putText(frame, "Restricted Area", (zx1, zy1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        weapon_detected = False

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:

                cls_id = int(box.cls[0])
                label = model.names[cls_id]

                # ---------------- WEAPON DETECTION ----------------
                if label in ["knife"]:
                    weapon_detected = True
                    cv2.putText(frame, "⚠ WEAPON DETECTED",
                                (20, 80),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 3)

                if label != "person":
                    continue

                person_count += 1
                track_id = int(box.id[0]) if box.id is not None else -1

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                current_positions[track_id] = (cx, cy)

                if track_id not in risk_score:
                    risk_score[track_id] = 0
                    last_event_time[track_id] = {}
                    alert_reasons[track_id] = set()

                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f"ID {track_id}", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # ---------------- RESTRICTED ZONE ----------------
                if zx1 < cx < zx2 and zy1 < cy < zy2:
                    risk_score[track_id] += RESTRICTED_WEIGHT
                    alert_reasons[track_id].add("Entered Restricted Area")

                    cv2.putText(frame, "Restricted Zone",
                                (x1, y2 + 60),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 0, 255), 2)

                # ---------------- LOITERING ----------------
                if track_id not in first_seen:
                    first_seen[track_id] = current_time

                duration = current_time - first_seen[track_id]

                if track_id in prev_positions:
                    px, py = prev_positions[track_id]
                    movement = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)

                    if movement < LOITER_MOVEMENT_TOLERANCE and duration > LOITER_TIME:
                        last_time = last_event_time[track_id].get("loiter", 0)

                        if current_time - last_time > LOITER_GAP:
                            risk_score[track_id] += LOITER_WEIGHT
                            last_event_time[track_id]["loiter"] = current_time
                            alert_reasons[track_id].add("Loitering detected")

                # ---------------- SPEED ----------------
                if track_id in prev_positions:
                    px, py = prev_positions[track_id]
                    distance = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)

                    if distance > SPEED_THRESHOLD:
                        last_time = last_event_time[track_id].get("speed", 0)

                        if current_time - last_time > SPEED_GAP:
                            risk_score[track_id] += SPEED_WEIGHT
                            last_event_time[track_id]["speed"] = current_time
                            alert_reasons[track_id].add("Abnormal speed movement")

                prev_positions[track_id] = (cx, cy)

        # ---------------- WEAPON BOOST ----------------
        if weapon_detected:
            for pid in risk_score:
                risk_score[pid] += WEAPON_BOOST
                alert_reasons[pid].add("Weapon presence in scene")

        # ---------------- CROWD ----------------
        if person_count > CROWD_LIMIT:
            if current_time - last_crowd_time > CROWD_GAP:
                for pid in risk_score:
                    risk_score[pid] += CROWD_WEIGHT
                    alert_reasons[pid].add("Crowd density exceeded")
                last_crowd_time = current_time

        # ---------------- FINAL ALERT CHECK ----------------
        for track_id in risk_score:

            risk_score[track_id] = max(0, risk_score[track_id] - RISK_DECAY)

            if (risk_score[track_id] >= RISK_THRESHOLD and
                    track_id not in alerted_persons):

                # Improved Threat Classification
                if risk_score[track_id] >= 12:
                    threat_level = "HIGH"
                elif risk_score[track_id] >= 7:
                    threat_level = "MEDIUM"
                else:
                    threat_level = "LOW"

                if len(alert_reasons[track_id]) > 1:
                    event_message = "Multiple suspicious behaviors detected"
                else:
                    event_message = list(alert_reasons[track_id])[0]

                # Insert into DB (UPDATED CALL)
                insert_alert(
                    track_id,
                    round(risk_score[track_id], 2),
                    environment,
                    event_message,
                    threat_level
                )

                alerted_persons.add(track_id)

                # Escalation Visual
                if threat_level == "HIGH":
                    cv2.rectangle(frame, (0, 0),
                                  (frame.shape[1], frame.shape[0]),
                                  (0, 0, 255), 8)
                    print(f"[ESCALATION] HIGH threat detected in {environment}")

                cv2.putText(frame, f"⚠ ALERT ({threat_level})",
                            (50, 150),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3)

        cv2.putText(frame, f"Persons: {person_count}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

        cv2.imshow("AI Surveillance Monitor", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()