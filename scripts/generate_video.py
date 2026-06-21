from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import json
import glob

# Load questions
with open('data/questions.json', 'r', encoding='utf-8') as f:
    QUESTIONS = json.load(f)

def find_hindi_font():
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]
    # Find any available noto font
    all_fonts = glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
    noto_fonts = [f for f in all_fonts if 'Noto' in f and 'Devanagari' in f]
    if noto_fonts:
        print(f"Found Devanagari font: {noto_fonts[0]}")
        return noto_fonts[0]
    noto_any = [f for f in all_fonts if 'Noto' in f]
    if noto_any:
        print(f"Found Noto font: {noto_any[0]}")
        return noto_any[0]
    for path in font_paths:
        if os.path.exists(path):
            return path
    print("No Hindi font found! Using default.")
    return None

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
        factor = 1 - (i / 1920) * 0.6
        r = int(bg_color[0] * factor * 0.4)
        g = int(bg_color[1] * factor * 0.4)
        b = int(bg_color[2] * factor * 0.4)
        draw.line([(0, i), (1080, i)], fill=(max(0,r), max(0,g), max(0,b)))

    # Load Hindi font
    font_path = find_hindi_font()

    try:
        if font_path:
            font_large = ImageFont.truetype(font_path, 52)
            font_medium = ImageFont.truetype(font_path, 42)
            font_small = ImageFont.truetype(font_path, 38)
            font_badge = ImageFont.truetype(font_path, 30)
            font_num = ImageFont.truetype(font_path, 52)
        else:
            raise Exception("No font")
    except Exception as e:
        print(f"Font error: {e}")
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
        font_badge = font_large
        font_num = font_large

    # Badge background
    draw.rounded_rectangle([60, 100, 700, 185], radius=25, fill=badge_color)
    draw.text((90, 122), badge_text, font=font_badge, fill="white")

    # Question number circle
    draw.ellipse([60, 210, 200, 350], fill="#FFD700")
    draw.text((82, 252), f"Q{q_num}", font=font_num, fill="#0D1117")

    # Question text wrap
    def wrap_text(text, max_chars=18):
        words = text.split(' ')
        lines = []
        current = ""
        for word in words:
            if len(current + word) > max_chars:
                if current:
                    lines.append(current.strip())
                current = word + " "
            else:
                current += word + " "
        if current:
            lines.append(current.strip())
        return lines

    # Draw question
    q_lines = wrap_text(question, 18)
    y = 390
    for line in q_lines[:7]:
        draw.text((60, y), line, font=font_large, fill="white")
        y += 78

    # Divider
    draw.rectangle([60, y+20, 1020, y+25], fill="#FFD700")

    # Answer label
    draw.text((60, y+50), "✅ उत्तर:", font=font_small, fill="#FFD700")

    # Answer text
    a_lines = wrap_text(answer, 22)
    y_ans = y + 110
    for line in a_lines[:4]:
        draw.text((60, y_ans), line, font=font_medium, fill="#00E676")
        y_ans += 62

    # Bottom bar
    draw.rectangle([0, 1820, 1080, 1920], fill="#FFD700")
    draw.text((350, 1845), "GK Adda", font=font_large, fill="#0D1117")

    img.save(filename)
    print(f"✅ Image: {filename}")

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
start_idx = ((day - 1) * 25) % len(QUESTIONS)

# Get today's 25 questions in order
today_questions = []
for i in range(25):
    idx = (start_idx + i) % len(QUESTIONS)
    today_questions.append(QUESTIONS[idx])

# Base question number
base_q_num = ((day - 1) * 25) + 1

os.makedirs("output_videos", exist_ok=True)

# Create 5 shorts
for short_num in range(5):
    short_questions = today_questions[short_num * 5: (short_num + 1) * 5]
    q_start = base_q_num + (short_num * 5)

    print(f"\n--- Short #{short_num+1} | Q{q_start} to Q{q_start+4} ---")

    video_files = []

    for i, q in enumerate(short_questions):
        q_num = q_start + i
        img_file = f"q_{q_num}.jpg"
        audio_file = f"q_{q_num}.mp3"
        video_file = f"q_{q_num}.mp4"

        create_question_image(q_num, q["q"], q["a"], q["type"], img_file)

        speak_text = f"प्रश्न {q_num}। {q['q']}। उत्तर है। {q['a']}"
        generate_audio(speak_text, audio_file)

        create_video(img_file, audio_file, video_file)
        video_files.append(video_file)

    # Merge into 1 short
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

    print(f"✅ Short #{short_num+1} ready: Q{q_start}-Q{q_start+4}")

print("\n✅ All 5 shorts created!")
