import io
import os
import time
import PIL.Image
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------
# GEMINI CLIENT
# ---------------------------------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------------------------------------------
# IMAGE STORAGE
# ---------------------------------------------------
ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# ---------------------------------------------------
# ESP32 UPLOAD ENDPOINT
# ---------------------------------------------------
@app.route('/upload', methods=['POST'])
def upload():
    image_bytes = request.data

    if not image_bytes:
        return "empty", 400

    try:
        # -------------------------
        # SAVE IMAGE
        # -------------------------
        filename = f"capture_{int(time.time())}.jpg"
        path = os.path.join(ASSETS_DIR, filename)

        with open(path, "wb") as f:
            f.write(image_bytes)

        print(f"[INFO] Image saved: {path}")

        # -------------------------
        # GEMINI PROMPT
        # -------------------------
        prompt = """
        Bu görseldeki soruları çöz.
        Sadece format: 1A,2B,3C şeklinde cevap ver.
        """

        image = PIL.Image.open(io.BytesIO(image_bytes))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image]
        )

        result = response.text.strip().replace(" ", "").replace("\n", "")

        print("[GEMINI RESULT]", result)

        return result, 200

    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------
# LIST ALL IMAGES (GALLERY)
# ---------------------------------------------------
@app.route('/gallery')
def gallery():
    files = sorted(os.listdir(ASSETS_DIR), reverse=True)

    html = "<h1>ESP32 Camera Gallery</h1><hr>"

    for f in files:
        url = f"/images/{f}"
        html += f"""
        <div>
            <p>{f}</p>
            <img src="{url}" width="300"/>
            <hr>
        </div>
        """

    return html

# ---------------------------------------------------
# SERVE IMAGE FILES
# ---------------------------------------------------
@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(ASSETS_DIR, filename)

# ---------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------
@app.route('/')
def home():
    return "ESP32 Server Running"

# ---------------------------------------------------
# RUN SERVER (RENDER COMPATIBLE)
# ---------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)