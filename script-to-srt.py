from flask import Flask, request, send_file, jsonify
import io
import re
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

WORDS_PER_SECOND = 4.0

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

def generate_srt(script, wps=WORDS_PER_SECOND):
    sentences = re.split(r'(?<=[.!?])\s+', script.strip())
    srt_output = ""
    current_time = 0.0
    index = 1

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        word_count = len(sentence.split())
        duration = word_count / wps
        start_time = format_timestamp(current_time)
        end_time = format_timestamp(current_time + duration)
        srt_output += f"{index}\n{start_time} --> {end_time}\n{sentence}\n\n"
        current_time += duration
        index += 1

    return srt_output.strip()

@app.route("/generate-srt", methods=["POST"])
def generate_srt_file():
    try:
        data = request.get_json(force=True)
        if not data or "script" not in data or "filename" not in data:
            logging.warning("Missing 'script' or 'filename'")
            return jsonify({"error": "Missing 'script' or 'filename'"}), 400

        script = data["script"]
        filename = data["filename"].strip()
        if not filename.endswith(".srt"):
            filename += ".srt"

        try:
            srt_content = generate_srt(script)
        except Exception as e:
            logging.exception("Error generating SRT")
            return jsonify({"error": "Failed to generate SRT", "details": str(e)}), 500

        # Convert to binary stream
        try:
            file_stream = io.BytesIO(srt_content.encode("utf-8"))
        except UnicodeEncodeError as e:
            logging.exception("Encoding error")
            return jsonify({"error": "Encoding error", "details": str(e)}), 500

        file_stream.seek(0)

        return send_file(
            file_stream,
            mimetype="application/x-subrip",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logging.exception("Unhandled exception")
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
