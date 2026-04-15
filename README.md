


# 🛡️ AI-Powered Real-Time Surveillance System

## 🚀 Overview
This project is an AI-based real-time surveillance system that monitors human activities and detects suspicious behavior using computer vision. It is designed for environments like airports, malls, and railway stations to enhance security and automate threat detection.

---

## 🧠 Key Features
- 👤 Real-time person detection and tracking using YOLOv8  
- ⏱️ Loitering detection based on time and movement  
- ⚡ Abnormal speed detection  
- 👥 Crowd density monitoring  
- 🚫 Restricted zone violation detection  
- 🔪 Weapon detection (knife)  
- 📊 Dynamic risk scoring system  
- 🚨 Threat classification (Low / Medium / High)  
- 🗂️ Alert logging system using database  

---

## 🛠️ Tech Stack
- **Programming:** Python  
- **AI/ML:** YOLOv8 (Ultralytics), OpenCV  
- **Frontend:** HTML, CSS  
- **Database:** SQLite (via Python)  

---

## 📁 Project Structure
```

├── app.py              # Main application (entry point)
├── detect.py           # Core detection & tracking logic
├── db.py               # Database operations (alerts storage)
├── main.py             # Optional runner script
├── templates/          # HTML pages (dashboard, alerts, login)
├── static/             # CSS styling

```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```

git clone [https://github.com/Saumya-01git/AI-Surveillance-System.git](https://github.com/your-username/AI-Surveillance-System.git)
cd AI-Surveillance-System

```

### 2️⃣ Install dependencies
```

pip install ultralytics opencv-python

```

### 3️⃣ Download YOLOv8 model
Download the model file manually:
```

yolov8n.pt

```
Place it in the root directory of the project.

---

## ▶️ How to Run
```

python app.py

```

---

## 📊 How It Works
- The system captures video input (camera or file)
- YOLOv8 detects and tracks individuals
- Behavioral analysis is applied:
  - Movement tracking
  - Time-based loitering
  - Speed analysis
  - Zone violations
- A **risk score** is calculated dynamically
- Alerts are generated when threshold is exceeded
- Results are displayed visually and stored in database

---

## 🎥 Demo
Sample videos were used to simulate:
- Crowd detection
- Loitering behavior
- Theft scenarios  

(*Videos not included due to size limitations*)

---

## ⚠️ Note
- The YOLOv8 model file (`yolov8n.pt`) is not included due to large size.
- Please download it separately from the official Ultralytics source.
- This project is for educational and research purposes.

---

## 👨‍💻 Author
**Saumya**  
B.Tech CSE (Cyber Security)  
VIT Chennai  

---

## ⭐ Future Improvements
- Multi-camera integration  
- Face recognition  
- Real-time alert notifications (SMS/Email)  
- Deployment on cloud systems
- Theft detection by analyzing the movement (suspicious behaviour)

```

---


