from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import json

# Load questions from JSON file
with open('data/questions.json', 'r', encoding='utf-8') as f:
    QUESTIONS = json.load(f)

def create_question_image(q_num, question, answer, q_type, filename):
    img = Image.new('RGB', (1080, 1920), color='#0D1117')
    draw = ImageDraw.Draw(img)

    # Colors by type
    if q_type == "gk":
        bg_color = (13, 71, 161)
        badge_text = "GK - सामान्य ज्ञान"
        badge_color = "#1565C0"
    elif q_type == "current":
        bg_color = (27, 94, 32)
        badge_text = "करंट अफेयर्स"
        badge_color = "#1B5E20"
    else:
        bg_color = (74, 20, 140)
        badge_text = "अजब दुनिया"
        badge_color = "#4A148C"

    # Background gradient
    for i in range(1920):
        r = int(bg_color[0] * (1 - i/1920) * 0.5)
        g = int(bg_color[1] * (1 - i/1920) * 0.5)
        b = int(bg_color[2] * (1 - i/1920) * 0.5)
        draw.line([(0, i), (1080, i)], fill=(r, g, b))

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_num = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
        font_badge = font_large
        font_num = font_large

    # Badge
    draw.rounded_rectangle([60, 100, 600, 180], radius=25, fill=badge_color)
    draw.text((90, 125), badge_text, font=font_badge, fill="white")

    # Question number circle
    draw.ellipse([60, 210, 190, 340], fill="#FFD700")
    draw.text((85, 245), f"Q{q_num}", font=font_num, fill="#0D1117")

    # Question text
    words = question.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test = current_line + word + " "
        if len(test) > 20:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test
    if current_line:
        lines.append(current_line.strip())

    y = 380
    for line in lines[:7]:
        draw.text((60, y), line, font=font_large, fill="white")
        y += 75

    # Divider line
    draw.rectangle([60, y+30, 1020, y+35], fill="#FFD700")

    # Answer label
    draw.text((60, y+60), "उत्तर:", font=font_small, fill="#FFD700")

    # Answer text
    ans_words = answer.split(' ')
    ans_lines = []
    current_line = ""
    for word in ans_words:
        test = current_line + word + " "
        if len(test) > 24:
            if current_line:
                ans_lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test
    if current_line:
        ans_lines.append(current_line.strip())

    y_ans = y + 120
    for line in ans_lines[:4]:
        draw.text((60, y_ans), line, font=font_medium, fill="#00E676")
        y_ans += 60

    # Bottom branding bar
    draw.rectangle([0, 1820, 1080, 1920], fill="#FFD700")
    draw.text((340, 1845), "GK Adda", font=font_large, fill="#0D1117")

    img.save(filename)
    print(f"Image created: {filename}")

def generate_audio(text, filename):
    tts = gTTS(text=text, lang='hi', slow=False)
    tts.save(filename)

def create_video(image_file, audio_file, output_file):
    subprocess.run([
        "ffmpeg",
        "-loop", "1",
        "-i", image_file,
        "-i", audio_file,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-y",
        output_file
    ])

# Calculate questions for today
day = int(os.environ.get("DAY_OFFSET", 1))
start_q = ((day - 1) * 25) % len(QUESTIONS)
today_questions = QUESTIONS[start_q:start_q+25]
if len(today_questions) < 25:
    today_questions += QUESTIONS[:25-len(today_questions)]

# Get today's 25 questions
today_questions = []
for i in range(25):
    idx = (start_q + i) % len(QUESTIONS)
    today_questions.append(QUESTIONS[idx])

# Create 5 shorts (5 questions each)
os.makedirs("output_videos", exist_ok=True)

for short_num in range(5):
    short_questions = today_questions[short_num * 5: (short_num + 1) * 5]
    q_start = ((day - 1) * 25) + (short_num * 5) + 1

    print(f"\n--- Creating Short #{short_num + 1} (Q{q_start}-Q{q_start+4}) ---")

    video_files = []

    for i, q in enumerate(short_questions):
        q_num = q_start + i
        img_file = f"q_{q_num}.jpg"
        audio_file = f"q_{q_num}.mp3"
        video_file = f"q_{q_num}.mp4"

        # Create image
        create_question_image(q_num, q["q"], q["a"], q["type"], img_file)

        # Create audio
        speak_text = f"प्रश्न {q_num}। {q['q']} ... उत्तर है। {q['a']}"
        generate_audio(speak_text, audio_file)

        # Create video clip
        create_video(img_file, audio_file, video_file)
        video_files.append(video_file)

    # Merge 5 clips into 1 short
    concat_file = f"concat_{short_num}.txt"
    with open(concat_file, "w") as f:
        for vf in video_files:
            f.write(f"file '{vf}'\n")

    output_short = f"output_videos/short_{short_num+1}.mp4"
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        "-y", output_short
    ])

    print(f"Short #{short_num+1} ready!")

print("\nAll 5 shorts created!")
