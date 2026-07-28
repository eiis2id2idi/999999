from flask import Flask, request, jsonify
import yt_dlp
import subprocess
import os

app = Flask(__name__)

COOKIE_FILE = "cookies.txt"


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "service": "YouTube Audio API",
        "cookies": os.path.exists(COOKIE_FILE)
    })


@app.route("/audio")
def audio():
    video_id = request.args.get("id")

    if not video_id:
        return jsonify({
            "success": False,
            "error": "Informe o id do vídeo"
        }), 400

    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "cookiefile": COOKIE_FILE,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        result = subprocess.run(
            [
                "yt-dlp",
                "--cookies",
                COOKIE_FILE,
                "--extractor-args",
                "youtube:player_client=android",
                "-f",
                "140",
                "-g",
                url
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return jsonify({
                "success": False,
                "error": result.stderr
            }), 500

        audio_url = result.stdout.strip()

        return jsonify({
            "success": True,
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "audio": audio_url
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
