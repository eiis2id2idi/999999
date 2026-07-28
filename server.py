from flask import Flask, request, jsonify
import subprocess
import yt_dlp

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "service": "YouTube Audio API"
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
        # Pega informações do vídeo
        ydl_opts = {
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Pega somente áudio m4a (itag 140)
        result = subprocess.run(
            [
                "yt-dlp",
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
