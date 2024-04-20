import os
import cv2
import base64
import requests
from pathlib import Path
from openai import OpenAI
from flask import Flask, send_file

# Flask setup
app = Flask(__name__)

@app.route('/speech', methods=['GET'])
def get_speech():
    speech_file_path = Path(__file__).parent / "speech.mp3"
    return send_file(speech_file_path, as_attachment=True)

# Image processing and OpenAI API
client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")

def encode_image(image):
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

def process_image_and_generate_speech():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not capture frame.")
        exit()

    base64_image = encode_image(frame)
    cap.release()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What’s in this image? in 20 words"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(response.json())

    speech_file_path = Path(__file__).parent / "speech.mp3"
    print(speech_file_path)

    print("Creating speech...")
    content = response.json()["choices"][0]["message"]["content"]
    print(content)
    response = client.audio.speech.create(
      model="tts-1",
      voice="shimmer",
      input=content,
    )
    print("Speech created.")
    response.stream_to_file(speech_file_path)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0')
    process_image_and_generate_speech()
