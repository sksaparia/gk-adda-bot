from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import json

# Load questions
with open('data/questions.json', 'r', encoding='utf-8') as f:
    QUESTIONS = json.load(f)

def create_short_image(short_num, questions, q_start, filename):
    # 1080x1920 portrait
    img = Image.new('RGB', (1080, 1920), color='#0A0A2E')
    draw = ImageDraw.Draw(img)

    # Find font
    import glob
    all_fonts = glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
    
    # Try Devanagari first
    hindi_fonts = [f for f in all_fonts if 'Devanagari' in f and 'Bold' in f]
    if not hindi_fonts:
        hindi_fonts = [f for f in all_fonts if 'Devanagari' in f]
    if not hindi_fonts:
        hindi_fonts = [f for f in all_fonts if 'Noto' in f and 'Bold' in f]
    if not hindi_fonts:
        hindi_fonts = [f for f in all_fonts if 'Noto' in f]
    
    font_path = hindi_fonts[0] if hindi_fonts else None
    print(f"Using font: {font_path}")

    try:
        if font_path:
            font_title = ImageFont.truetype(font_path, 48)
            font_q = ImageFont.truetype(font_path, 36)
            font_a = ImageFont.truetype(font_path, 34)
            font_header = ImageFont.truetype(font_path, 42)
        else:
            raise Exception("No font")
    except:
        font_title = ImageFont.load_default()
        font_q = font_title
        font_a = font_title
        font_header = font_title

    # Header bar
    draw.rectangle([0, 0, 1080, 130], fill="#1A1A5E")
    draw.text((50, 35), "🧠 आज के GK सवाल", font=font_header, fill="#FFD700")
    draw.text((700, 40), f"GK Adda", font=font_q, fill="#FFD700")

    # Draw 5 questions
    y = 160
    colors = ["#FFD700", "#00E676", "#FF6B6B", "#64B5F6", "#FF9800"]
    
    for i, q in enumerate(questions):
        q_num = q_start + i
        
        # Question background
        draw.rounded_rectangle([30, y, 1050, y+220], radius=20, fill="#1A1A3E")
        
        # Q number badge
        draw.ellipse([45, y+15, 115, y+85], fill=colors[i])
        draw.text((58, y+28), f"Q{q_num}", font=font_q, fill="#0A0A2E")
        
        # Question text
        q_text = q["q"]
        if len(q_text) > 35:
            q_text = q_text[:35] + "..."
        draw.text((130, y+20), q_text, font=font_q, fill="white")
        
        # Answer
        draw.text((130, y+90), "✅ " + q["a"][:45], font=font_a, fill=colors[i])
        
        # Type badge
        type_text = "GK" if q["type"] == "gk" else ("CA" if q["type"] == "current" else "FACT")
        draw.rounded_rectangle([900, y+150, 1040, y+200], radius=10, fill=colors[i])
        draw.text((920, y+158), type_text, font=font_q, fill="#0A0A2E")
        
        y += 240

    # Bottom bar
    draw.rectangle([0, 1850, 1080, 1920], fill="#FFD700")
    draw.text((350, 1860), "Subscribe करें! 🔔", font=font_q, fill="#0A0A2E")

    img.save(filename)
    print(f"✅ Image saved: {filename}")

def generate_audio(questions, q_start, filename):
    text = "आज के जीके सवाल। "
    for i, q in enumerate(questions):
        q_num = q_start + i
        text += f"सवाल {q_num}। {q['q']}। जवाब। {q['a']}। "
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

# Day calculation
day = int(os.environ.get("DAY_OFFSET", 1))
start_idx = ((day - 1) * 25) % len(QUESTIONS)
base_q_num = ((day - 1) * 25) + 1

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

    print(f"\n--- Short #{short_num+1} | Q{q_start}-Q{q_start+4} ---")

    img_file = f"short_{short_num+1}.jpg"
    audio_file = f"short_{short_num+1}.mp3"
    output_file = f"output_videos/short_{short_num+1}.mp4"

    create_short_image(short_num+1, short_questions, q_start, img_file)
    generate_audio(short_questions, q_start, audio_file)
    create_video(img_file, audio_file, output_file)

    print(f"✅ Short #{short_num+1} done!")

print("\n✅ All 5 shorts ready!")
