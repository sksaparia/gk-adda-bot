from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import json
import glob

# Load questions
with open('data/questions.json', 'r', encoding='utf-8') as f:
    QUESTIONS = json.load(f)

def create_short_image(questions, q_start, filename):
    img = Image.new('RGB', (1080, 1920), color='#0A0A2E')
    draw = ImageDraw.Draw(img)

    # Find best font
    all_fonts = glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
    font_path = None
    for keyword in ['DejaVuSans-Bold', 'DejaVuSans', 'NotoSans-Bold', 'NotoSans']:
        matches = [f for f in all_fonts if keyword in f]
        if matches:
            font_path = matches[0]
            break

    print(f"Font: {font_path}")

    try:
        f_header = ImageFont.truetype(font_path, 52)
        f_q = ImageFont.truetype(font_path, 38)
        f_a = ImageFont.truetype(font_path, 36)
        f_small = ImageFont.truetype(font_path, 30)
        f_badge = ImageFont.truetype(font_path, 32)
    except:
        f_header = ImageFont.load_default()
        f_q = f_header
        f_a = f_header
        f_small = f_header
        f_badge = f_header

    # Header
    draw.rectangle([0, 0, 1080, 140], fill="#1A1A6E")
    draw.text((40, 42), "Aaj ke GK Sawaal", font=f_header, fill="#FFD700")
    draw.text((790, 52), "GK Adda", font=f_small, fill="#FFD700")

    # Colors
    q_colors = ["#FFD700", "#00E676", "#FF6B6B", "#64B5F6", "#FF9800"]
    ans_colors = ["#00E676", "#64B5F6", "#FF8A65", "#80CBC4", "#CE93D8"]
    bg_colors = ["#0D1F0D", "#0D0D1F", "#1F0D0D", "#0D1F1F", "#1F0D1F"]

    y = 155
    box_h = 338

    for i, q in enumerate(questions):
        q_num = q_start + i

        # Box background
        draw.rounded_rectangle([15, y, 1065, y+box_h], radius=20, fill=bg_colors[i])

        # Q number circle
        draw.ellipse([25, y+12, 115, y+102], fill=q_colors[i])
        draw.text((38, y+30), f"Q{q_num}", font=f_badge, fill="#000000")

        # Question text wrap
        words = q["q"].split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + w) > 27:
                if cur:
                    lines.append(cur.strip())
                cur = w + " "
            else:
                cur += w + " "
        if cur:
            lines.append(cur.strip())

        ty = y + 15
        for line in lines[:3]:
            draw.text((125, ty), line, font=f_q, fill="white")
            ty += 50

        # Divider
        draw.rectangle([125, y+box_h-105, 1050, y+box_h-100], fill=q_colors[i])

        # Answer
        ans = "Ans: " + q["a"][:48]
        draw.text((125, y+box_h-92), ans, font=f_a, fill=ans_colors[i])

        # Type badge
        badge = {"gk": "GK", "current": "CA", "strange": "FACT"}.get(q["type"], "GK")
        draw.rounded_rectangle([940, y+box_h-55, 1055, y+box_h-12], radius=8, fill=q_colors[i])
        draw.text((955, y+box_h-48), badge, font=f_small, fill="#000000")

        y += box_h + 12

    # Bottom bar
    draw.rectangle([0, 1875, 1080, 1920], fill="#FFD700")
    draw.text((280, 1882), "Subscribe karein! Bell dabao! GK Adda", font=f_small, fill="#000000")

    img.save(filename)
    print(f"✅ Image: {filename}")

def generate_audio(questions, q_start, filename):
    text = "Aaj ke GK sawaal. "
    for i, q in enumerate(questions):
        q_num = q_start + i
        text += f"Sawaal {q_num}. {q['q']}. Jawab hai. {q['a']}. "
    tts = gTTS(text=text, lang='hi', slow=False)
    tts.save(filename)
    print(f"✅ Audio: {filename}")

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
    print(f"✅ Video: {output_file}")

# Day calculation — Q1 se start
day = int(os.environ.get("DAY_OFFSET", 1))
actual_day = ((day - 1) % 60) + 1
start_idx = ((actual_day - 1) * 25) % len(QUESTIONS)
base_q_num = ((actual_day - 1) * 25) + 1

print(f"Day: {day} | Actual Day: {actual_day} | Q{base_q_num} to Q{base_q_num+24}")

# Get 25 questions in order
today_questions = []
for i in range(25):
    idx = (start_idx + i) % len(QUESTIONS)
    today_questions.append(QUESTIONS[idx])

os.makedirs("output_videos", exist_ok=True)

# Create 5 shorts
for short_num in range(5):
    short_questions = today_questions[short_num * 5: (short_num + 1) * 5]
    q_start = base_q_num + (short_num * 5)

    print(f"\n=== Short #{short_num+1} | Q{q_start}-Q{q_start+4} ===")

    img_file = f"short_{short_num+1}.jpg"
    audio_file = f"short_{short_num+1}.mp3"
    out_file = f"output_videos/short_{short_num+1}.mp4"

    create_short_image(short_questions, q_start, img_file)
    generate_audio(short_questions, q_start, audio_file)
    create_video(img_file, audio_file, out_file)

    print(f"✅ Short #{short_num+1} done!")

print("\n✅ All 5 shorts ready!")
