import os
import glob
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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
            "tags": [
                "gk", "general knowledge", "current affairs",
                "gk in hindi", "gk questions", "gk adda",
                "ssc gk", "upsc gk", "railway gk",
                "gk shorts", "gk quiz", "daily gk"
            ],
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

# Get day number
day = int(os.environ.get("DAY_OFFSET", 1))
start_q = (day - 1) * 25 + 1

# Upload all 5 shorts
youtube = get_youtube_service()

video_files = sorted(glob.glob("output_videos/short_*.mp4"))

for i, video_file in enumerate(video_files):
    short_num = i + 1
    q_start = start_q + (i * 5)
    q_end = q_start + 4

    title = f"GK Quiz 🧠 Q{q_start}-Q{q_end} | सामान्य ज्ञान | GK Adda #{day*5 - 5 + short_num}"

    description = f"""Q{q_start} से Q{q_end} तक के कठिन प्रश्न!

🧠 सामान्य ज्ञान | 📰 करंट अफेयर्स | 🌍 अजब दुनिया

✅ रोज़ 5 नए Shorts — GK Adda पर!
🔔 Subscribe करें और Bell Icon दबाएं!

#GKAdda #GKinHindi #CurrentAffairs #GKShorts #SSCGK #UPSCGK #RailwayGK #DailyGK #GKQuiz #GeneralKnowledge
"""

    print(f"Uploading Short #{short_num}: Q{q_start}-Q{q_end}")
    upload_video(youtube, video_file, title, description)

print("\n✅ All 5 shorts uploaded to GK Adda!")
