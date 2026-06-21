from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import json

# Load questions
with open('data/questions.json', 'r', encoding='utf-8') as f:
    QUESTIONS = json.load(f)

# Transliterate common Hindi words to Roman for display
def hindi_to_display(text):
    # Keep text as is but use English fallback font
    return text

def create_short_image(questions, q_start, filename):
    # 1080x1920 portrait - YouTube Shorts
    img = Image.new('RGB', (1080, 1920), color='#0A0A2E')
    draw = ImageDraw.Draw(img)

    # Find best available font
    import glob
    all_fonts = glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
    
    # Priority: Devanagari > Noto > DejaVu > Default
    font_path = None
    for keyword in ['Devanagari', 'NotoSans-Bold', 'NotoSans', 'DejaVuSans-Bold', 'DejaVuSans']:
        matches = [f for f in all_fonts if keyword in f]
        if matches:
            font_path = matches[0]
            break
    
    print(f"Font: {font_path}")

    try:
        f_header = ImageFont.truetype(font_path, 50) if font_path else ImageFont.load_default()
        f_q = ImageFont.truetype(font_path, 38) if font_path else ImageFont.load_default()
        f_a = ImageFont.truetype(font_path, 36) if font_path else ImageFont.load_default()
        f_small = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()
    except:
        f_header = ImageFont.load_default()
        f_q = f_header
        f_a = f_header
        f_small = f_header

    # ---- HEADER ----
    draw.rectangle([0, 0, 1080, 140], fill="#1A1A6E")
    draw.text((40, 45), "Aaj ke GK Sawaal", font=f_header, fill="#FFD700")
    draw.text((780, 55), "GK Adda", font=f_small, fill="#FFD700")

    # ---- 5 QUESTIONS ----
    colors_bg = ["#1A2A1A", "#1A1A3A", "#2A1A1A", "#1A2A2A", "#2A1A2A"]
    colors_ans = ["#00E676", "#64B5F6", "#FF8A65", "#80CBC4", "#CE93D8"]
    q_colors = ["#FFD700", "#00E676", "#FF6B6B", "#64B5F6", "#FF9800"]

    y = 155
    box_height = 340

    for i, q in enumerate(questions):
        q_num = q_start + i

        # Question box
        draw.rounded_rectangle([20, y, 1060, y+box_height], radius=18, fill=colors_bg[i])

        # Q number badge
        draw.ellipse([30, y+15, 110, y+95], fill=q_colors[i])
        draw.text((45, y+30), f"Q{q_num}", font=f_q, fill="#000000")

        # Question text - wrap at 28 chars
        q_text = q["q"]
        words = q_text.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + w) > 28:
                if cur: lines.append(cur.strip())
                cur = w + " "
            else:
                cur += w + " "
        if cur: lines.append(cur.strip())

        ty = y + 18
        for line in lines[:3]:
            draw.text((120, ty), line, font=f_q, fill="white")
            ty += 48

        # Answer
        ans_text = "Ans: " + q["a"][:50]
        draw.text((120, y + box_height - 90), ans_text, font=f_a, fill=colors_ans[i])

        # Type badge
        type_map = {"gk": "GK", "current": "CA", "strange": "FACT"}
        badge = type_map.get(q["type"], "GK")
        draw.rounded_rectangle([900, y+box_height-60, 1040, y+box_height-15], radius=10, fill=q_colors[i])
        draw.text((920, y+box_height-52), badge, font=f_small, fill="#000000")

        y += box_height + 15

    # ---- BOTTOM BAR ----
    draw.rectangle([0, 1880, 1080, 1920], fill="#FFD700")
    draw.text((320, 1885), "Subscribe karein! GK Adda", font=f_small, fill="#000000")

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
    result = subprocess.run([
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
    ], capture_output=True)
    print(f"✅ Video: {output_file}")

# ---- MAIN ----
day = int(os.environ.get("DAY_OFFSET", 1))

# Q1 se start — Day 1 = Q1-Q25, Day 2 = Q26-Q50
start_idx = ((day - 1) * 25) % len(QUESTIONS)
base_q_num = ((day - 1) * 25) + 1

print(f"Day: {day} | Questions: Q{base_q_num} to Q{base_q_num+24}")

# Get 25 questions in order
today_questions = []
for i in range(25):
    idx = (start_idx + i) % len(QUESTIONS)
    today_questions.append(QUESTIONS[idx])

os.makedirs("output_videos", exist_ok=True)

# Create 5 shorts (5 questions each)
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

    print(f"✅ Short #{short_num+1} complete!")

print("\n✅ All 5 shorts done!")
