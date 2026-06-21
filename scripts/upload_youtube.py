import os
import glob
import time
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

VIDEOS_TITLES = [
    "GK Quiz Q{s}-Q{e} | Aaj ke Sawaal | GK Adda #{n}",
]

TAGS = [
    "gk", "general knowledge", "current affairs",
    "gk in hindi", "gk questions", "gk adda",
    "ssc gk", "upsc gk", "railway gk",
    "gk shorts", "gk quiz", "daily gk"
]

def get_youtube_service():
    creds = google.oauth2.credentials.Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, video_file, title, description):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": TAGS,
            "categoryId": "27",
            "defaultLanguage": "hi"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        video_file,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024*1024*5
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = request.execute()
    print(f"✅ Uploaded: {title}")
    print(f"✅ Video ID: {response['id']}")
    return response['id']

# Day calculation
day = int(os.environ.get("DAY_OFFSET", 1))
actual_day = ((day - 1) % 60) + 1
base_q_num = ((actual_day - 1) * 25) + 1

print(f"Day: {day} | Actual Day: {actual_day} | Starting Q{base_q_num}")

youtube = get_youtube_service()
video_files = sorted(glob.glob("output_videos/short_*.mp4"))

for i, video_file in enumerate(video_files):
    short_num = i + 1
    q_start = base_q_num + (i * 5)
    q_end = q_start + 4
    video_num = (actual_day - 1) * 5 + short_num

    title = f"GK Quiz Q{q_start}-Q{q_end} | Aaj ke Sawaal | GK Adda #{video_num}"

    description = f"""Q{q_start} se Q{q_end} tak ke tough sawaal!

🧠 Samanya Gyan | 📰 Current Affairs | 🌍 Ajab Duniya

✅ Roz 5 naye Shorts — GK Adda par!
🔔 Subscribe karein aur Bell Icon dabayein!

#GKAdda #GKinHindi #CurrentAffairs #GKShorts #SSCGK #UPSCGK #RailwayGK #DailyGK #GKQuiz
"""

    print(f"\nUploading Short #{short_num}: Q{q_start}-Q{q_end}")
    upload_video(youtube, video_file, title, description)
    
    # Wait between uploads
    if short_num < len(video_files):
        print("Waiting 15 seconds...")
        time.sleep(15)

print("\n✅ All 5 shorts uploaded to GK Adda!")
