import io
import os
import time
import PIL.Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.getenv("AIzaSyC2KNRgn_Ks1C4gndTP4Xgrwq9asdSuIkc"))

ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    image_bytes = request.data

    if not image_bytes:
        return "empty", 400

    try:
        # save debug image
        path = f"{ASSETS_DIR}/{int(time.time())}.jpg"
        with open(path, "wb") as f:
            f.write(image_bytes)

        prompt = """
        Bu görseldeki soruları çöz.
        Sadece format: 1A,2B,3C
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, PIL.Image.open(io.BytesIO(image_bytes))]
        )

        return response.text.strip()

    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))