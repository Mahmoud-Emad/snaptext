import logging
import os
import tempfile

from flask import Flask, render_template, request, send_from_directory

from core.tool import extract_text, get_text_confidence

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    logger.info("Serving index page")
    return render_template("index.html")


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)


@app.route("/upload", methods=["POST"])
def upload():
    logger.info("Upload request received")

    if "file" not in request.files:
        logger.warning("No file in request")
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    if file.filename == "":
        logger.warning("Empty filename provided")
        return {"error": "Empty filename"}, 400

    logger.info(f"Processing file: {file.filename}")
    # Use secure temporary directory
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(file.filename)[1]
    ) as tmp_file:
        upload_path = tmp_file.name
        file.save(upload_path)

    try:
        text = extract_text(upload_path)
        confidence_info = get_text_confidence(upload_path)
        logger.info(f"Text extraction successful for {file.filename}")
        logger.info(f"OCR confidence: {confidence_info}")

        os.remove(upload_path)

        return {"text": text, "confidence": confidence_info, "filename": file.filename}
    except Exception as e:
        logger.error(f"Error extracting text from {file.filename}: {str(e)}")
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return {"error": f"Failed to extract text: {str(e)}"}, 500


if __name__ == "__main__":
    logger.info("Starting SnapText OCR Server...")
    logger.info("Server will be available at http://127.0.0.1:5000")
    # Use environment variable to control debug mode for security
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, port=5000, host="127.0.0.1")
