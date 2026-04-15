from detect import run_detection

# ---------------- ENVIRONMENT SELECTION ----------------
print("\nSelect Environment")
print("1 → Railway Station")
print("2 → Shopping Mall")
print("3 → Airport\n")

env_choice = input("Enter environment choice: ")

if env_choice == "1":
    environment = "Railway Station"
elif env_choice == "2":
    environment = "Shopping Mall"
elif env_choice == "3":
    environment = "Airport"
else:
    print("Invalid environment selected.")
    exit()


# ---------------- VIDEO SELECTION ----------------
print("\nSelect Video")
print("1 → crowd.mp4")
print("2 → theft.mp4")
print("3 → run.mp4")
print("4 → loiter.mp4\n")

video_choice = input("Enter video choice: ")

if video_choice == "1":
    video = "crowd.mp4"
elif video_choice == "2":
    video = "theft.mp4"
elif video_choice == "3":
    video = "run.mp4"
elif video_choice == "4":
    video = "loiter.mp4"
else:
    print("Invalid video selected.")
    exit()


# ---------------- RUN DETECTION ----------------
print(f"\nStarting detection in {environment} mode using {video}...\n")

run_detection(video, environment)