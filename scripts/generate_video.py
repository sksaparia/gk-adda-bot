from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import glob

# 500+ tough questions bank
QUESTIONS = [
    # GK Questions (Tough)
    {"q": "भारत के किस राज्य में सबसे अधिक जिले हैं?", "a": "उत्तर प्रदेश (75 जिले)", "type": "gk"},
    {"q": "भारतीय संविधान में मूल रूप से कितनी अनुसूचियां थीं?", "a": "8 अनुसूचियां", "type": "gk"},
    {"q": "किस भारतीय राज्य की समुद्री सीमा सबसे लंबी है?", "a": "गुजरात", "type": "gk"},
    {"q": "भारत का सबसे पुराना तेल रिफाइनरी कहाँ है?", "a": "डिगबोई, असम (1901)", "type": "gk"},
    {"q": "किस मुगल बादशाह ने तंबाकू पर प्रतिबंध लगाया था?", "a": "जहाँगीर", "type": "gk"},
    {"q": "भारत में पहली बार जनगणना कब हुई थी?", "a": "1872 में", "type": "gk"},
    {"q": "किस देश को 'हजार झीलों की भूमि' कहा जाता है?", "a": "फिनलैंड", "type": "gk"},
    {"q": "विश्व का सबसे बड़ा लोकतंत्र कौन सा है?", "a": "भारत", "type": "gk"},
    {"q": "भारत के किस राज्य में सबसे पहले सूर्योदय होता है?", "a": "अरुणाचल प्रदेश", "type": "gk"},
    {"q": "संयुक्त राष्ट्र की स्थापना किस वर्ष हुई?", "a": "1945", "type": "gk"},
    {"q": "भारत का राष्ट्रीय जलीय जीव कौन है?", "a": "गंगा डॉल्फिन", "type": "gk"},
    {"q": "किस ग्रह को 'लाल ग्रह' कहा जाता है?", "a": "मंगल", "type": "gk"},
    {"q": "भारत में सबसे लंबी नदी कौन सी है?", "a": "गंगा", "type": "gk"},
    {"q": "विश्व का सबसे छोटा देश कौन सा है?", "a": "वेटिकन सिटी", "type": "gk"},
    {"q": "भारत का क्षेत्रफल कितना है?", "a": "32,87,263 वर्ग किमी", "type": "gk"},
    {"q": "किस विटामिन की कमी से रतौंधी होती है?", "a": "विटामिन A", "type": "gk"},
    {"q": "भारत में कुल कितने उच्च न्यायालय हैं?", "a": "25", "type": "gk"},
    {"q": "कौन सा देश सबसे अधिक देशों के साथ सीमा साझा करता है?", "a": "चीन (14 देश)", "type": "gk"},
    {"q": "भारत का सबसे बड़ा बंदरगाह कौन सा है?", "a": "मुंबई बंदरगाह", "type": "gk"},
    {"q": "किस भारतीय वैज्ञानिक को 'मिसाइल मैन' कहा जाता है?", "a": "डॉ. एपीजे अब्दुल कलाम", "type": "gk"},

    # Current Affairs (Tough)
    {"q": "2024 में भारत के 18वें लोकसभा चुनाव में किस पार्टी को सर्वाधिक सीटें मिलीं?", "a": "BJP (240 सीटें)", "type": "current"},
    {"q": "2024 में किस देश ने पहली बार ICC T20 World Cup जीता?", "a": "भारत", "type": "current"},
    {"q": "2024 के पेरिस ओलंपिक में भारत ने कुल कितने पदक जीते?", "a": "6 पदक", "type": "current"},
    {"q": "2024 में किसे भारत रत्न से सम्मानित किया गया?", "a": "LK आडवाणी, MS स्वामीनाथन, चरण सिंह, PV नरसिम्हा राव, कर्पूरी ठाकुर", "type": "current"},
    {"q": "2024 में भारत का GDP विकास दर कितना रहा?", "a": "8.2%", "type": "current"},
    {"q": "2024 में कौन सा देश BRICS का नया सदस्य बना?", "a": "सऊदी अरब, UAE, इथियोपिया, ईरान, मिस्र, अर्जेंटीना", "type": "current"},
    {"q": "2024 में किस भारतीय को Nobel Prize मिला?", "a": "किसी को नहीं", "type": "current"},
    {"q": "2024 में भारत का सबसे बड़ा IPO कौन सा था?", "a": "Hyundai India IPO", "type": "current"},
    {"q": "2024 में किस देश में AI को कानूनी दर्जा दिया गया?", "a": "यूरोपीय संघ (EU AI Act)", "type": "current"},
    {"q": "2025 में भारत के नए RBI गवर्नर कौन बने?", "a": "संजय मल्होत्रा", "type": "current"},

    # Strange World Facts (Tough)
    {"q": "क्या आप जानते हैं? ऑक्टोपस के कितने दिल होते हैं?", "a": "3 दिल! दो गिल्स के लिए और एक पूरे शरीर के लिए 🐙", "type": "strange"},
    {"q": "क्या आप जानते हैं? किस देश में सूरज 6 महीने नहीं डूबता?", "a": "नॉर्वे — इसे 'Land of Midnight Sun' कहते हैं 🌞", "type": "strange"},
    {"q": "क्या आप जानते हैं? शहद कभी खराब क्यों नहीं होता?", "a": "शहद में हाइड्रोजन पेरोक्साइड होता है जो बैक्टीरिया को मारता है 🍯", "type": "strange"},
    {"q": "क्या आप जानते हैं? मानव शरीर में कितनी हड्डियां होती हैं?", "a": "206 हड्डियां — बच्चों में 270 होती हैं जो बाद में जुड़ जाती हैं 🦴", "type": "strange"},
    {"q": "क्या आप जानते हैं? कौन सा जानवर कभी नहीं सोता?", "a": "बुलफ्रॉग — यह कभी नहीं सोता! 🐸", "type": "strange"},
    {"q": "क्या आप जानते हैं? एक दिन में कितनी बार दिल धड़कता है?", "a": "लगभग 1,00,000 बार! 💓", "type": "strange"},
    {"q": "क्या आप जानते हैं? किस धातु को हाथ से काटा जा सकता है?", "a": "सोडियम — इतना नरम होता है 🔪", "type": "strange"},
    {"q": "क्या आप जानते हैं? पृथ्वी पर सबसे गहरी जगह कौन सी है?", "a": "मारियाना ट्रेंच — 11,034 मीटर गहरी 🌊", "type": "strange"},
    {"q": "क्या आप जानते हैं? किस पेड़ की लकड़ी पानी में डूब जाती है?", "a": "आयरनवुड — यह पानी से भारी होती है 🌳", "type": "strange"},
    {"q": "क्या आप जानते हैं? मनुष्य के DNA का कितना % केले से मिलता है?", "a": "60% DNA केले से मिलता है! 🍌", "type": "strange"},
]

def create_question_image(q_num, question, answer, q_type, filename):
    # 1080x1920 portrait (YouTube Shorts)
    img = Image.new('RGB', (1080, 1920), color='#0D1117')
    draw = ImageDraw.Draw(img)

    # Background gradient effect
    for i in range(1920):
        alpha = int(255 * (i / 1920) * 0.3)
        if q_type == "gk":
            draw.line([(0, i), (1080, i)], fill=(13, 71, 161))
        elif q_type == "current":
            draw.line([(0, i), (1080, i)], fill=(27, 94, 32))
        else:
            draw.line([(0, i), (1080, i)], fill=(74, 20, 140))

    # Dark overlay
    overlay = Image.new('RGB', (1080, 1920), color='#0D1117')
    img = Image.blend(img, overlay, 0.7)
    draw = ImageDraw.Draw(img)

    # Type badge
    if q_type == "gk":
        badge_color = "#1565C0"
        badge_text = "🧠 सामान्य ज्ञान"
    elif q_type == "current":
        badge_color = "#1B5E20"
        badge_text = "📰 करंट अफेयर्स"
    else:
        badge_color = "#4A148C"
        badge_text = "🌍 अजब दुनिया"

    # Draw badge
    draw.rounded_rectangle([80, 120, 500, 200], radius=25, fill=badge_color)

    # Question number
    draw.ellipse([80, 240, 200, 360], fill="#FFD700")

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
        font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_num = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
        font_badge = font_large
        font_num = font_large

    # Badge text
    draw.text((100, 140), badge_text, font=font_badge, fill="white")

    # Q number
    draw.text((115, 265), f"Q{q_num}", font=font_num, fill="#0D1117")

    # Question text (wrap)
    words = question.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if len(test_line) > 22:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line.strip())

    y_pos = 420
    for line in lines[:6]:
        draw.text((80, y_pos), line, font=font_large, fill="white")
        y_pos += 80

    # Divider
    draw.rectangle([80, y_pos + 40, 1000, y_pos + 45], fill="#FFD700")

    # Answer section
    draw.text((80, y_pos + 80), "✅ उत्तर:", font=font_small, fill="#FFD700")

    # Answer text (wrap)
    ans_words = answer.split(' ')
    ans_lines = []
    current_line = ""
    for word in ans_words:
        test_line = current_line + word + " "
        if len(test_line) > 25:
            if current_line:
                ans_lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test_line
    if current_line:
        ans_lines.append(current_line.strip())

    y_ans = y_pos + 150
    for line in ans_lines[:4]:
        draw.text((80, y_ans), line, font=font_medium, fill="#00E676")
        y_ans += 65

    # Bottom branding
    draw.rectangle([0, 1800, 1080, 1920], fill="#FFD700")
    draw.text((350, 1840), "GK Adda", font=font_large, fill="#0D1117")

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

# Calculate which questions to use today
day = int(os.environ.get("DAY_OFFSET", 1))
start_q = (day - 1) * 25  # Day 1 = 0-24, Day 2 = 25-49

# Get today's 25 questions
today_questions = []
for i in range(25):
    idx = (start_q + i) % len(QUESTIONS)
    today_questions.append(QUESTIONS[idx])

# Create 5 shorts (5 questions each)
os.makedirs("output_videos", exist_ok=True)

for short_num in range(5):
    short_questions = today_questions[short_num * 5: (short_num + 1) * 5]
    q_start = start_q + (short_num * 5) + 1

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

    output_short = f"output_videos/short_{short_num + 1}_Q{q_start}-Q{q_start+4}.mp4"
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        "-y", output_short
    ])

    print(f"✅ Short #{short_num + 1} ready: {output_short}")

print("\n✅ All 5 shorts created!")
