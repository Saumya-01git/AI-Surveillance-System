import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="surveillance_system"
    )


def insert_alert(track_id, risk_score, environment, event_message, threat_level):

    db = get_connection()
    cursor = db.cursor()

    # 1️⃣ Insert or update person
    cursor.execute("""
        INSERT INTO persons_tracked (track_id, first_detected, last_detected, total_risk)
        VALUES (%s, NOW(), NOW(), %s)
        ON DUPLICATE KEY UPDATE
            last_detected = NOW(),
            total_risk = total_risk + %s
    """, (track_id, risk_score, risk_score))

    # 2️⃣ Get camera id
    cursor.execute("""
        SELECT camera_id FROM cameras
        WHERE environment_type=%s LIMIT 1
    """, (environment,))
    cam = cursor.fetchone()
    camera_id = cam[0] if cam else 1

    # 3️⃣ Extract clean event name
    clean_event = event_message.split("(")[0].strip()

    cursor.execute("""
        SELECT event_id FROM events
        WHERE event_name=%s LIMIT 1
    """, (clean_event,))
    evt = cursor.fetchone()
    event_id = evt[0] if evt else 1

    # 4️⃣ Insert alert (UPDATED)
    cursor.execute("""
        INSERT INTO alerts (camera_id, track_id, event_id, risk_score, threat_level)
        VALUES (%s, %s, %s, %s, %s)
    """, (camera_id, track_id, event_id, risk_score, threat_level))

    db.commit()
    cursor.close()
    db.close()

    print(f"Alert inserted successfully! Threat Level: {threat_level}")