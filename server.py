from flask import Flask, request, jsonify
import yt_dlp
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
                    "player_client": [
                        "android"
                    ]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                url,
                download=False
            )

        audio_url = None

        # Procura qualquer formato somente com áudio
        for fmt in info.get("formats", []):
            acodec = fmt.get("acodec")

            if (
                acodec
                and acodec != "none"
                and fmt.get("url")
            ):
                audio_url = fmt["url"]
                break

        if not audio_url:
            return jsonify({
                "success": False,
                "error": "Nenhum áudio encontrado",
                "formats": len(info.get("formats", []))
            }), 500

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
