from flask import Flask, request, send_file, jsonify
from gtts import gTTS
import os
import time

app = Flask(__name__)

SAVE_FOLDER = os.path.join(os.getcwd(), "audio_files")
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON data"}), 400

        text = data.get('text')
        filename = data.get('filename', 'speech.mp3')

        if not text:
            return jsonify({"error": "Text is required"}), 400

        filename = filename.strip()
        if not filename.endswith('.mp3'):
            filename += '.mp3'

        output_path = os.path.join(SAVE_FOLDER, filename)

        # Generate and save speech
        try:
            tts = gTTS(text=text, lang='en')
            tts.save(output_path)
        except Exception as e:
            return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

        time.sleep(0.3)  # Allow filesystem to flush

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return jsonify({"error": "Audio file not created properly"}), 500

        return send_file(
            output_path,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
