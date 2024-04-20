from flask import Flask, send_file
from pathlib import Path

app = Flask(__name__)

@app.route('/speech', methods=['GET'])
def get_speech():
    speech_file_path = Path(__file__).parent / "speech.mp3"
    return send_file(speech_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
