from flask import Flask, request, send_from_directory, render_template, after_this_request
import os
from ebooklib import epub
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/create", methods=['POST'])
def create():
    try:
        cover_img = request.files.get('cover_image')
        original_epub = request.files.get('original')
        if not cover_img or not original_epub:
            return "Please upload both the cover image and the original EPUB file.", 400

        cover_img_path = os.path.join(UPLOAD_FOLDER, cover_img.filename)
        original_epub_path = os.path.join(UPLOAD_FOLDER, original_epub.filename)
        cover_img.save(cover_img_path)
        original_epub.save(original_epub_path)

        # Assume processing is successful and an EPUB is created
        new_epub_path = os.path.join(UPLOAD_FOLDER, 'new_epub_file.epub')

        @after_this_request
        def cleanup_files(response):
            os.remove(cover_img_path)
            os.remove(original_epub_path)
            os.remove(new_epub_path)
            return response

        return send_from_directory(directory=UPLOAD_FOLDER, filename=os.path.basename(new_epub_path), as_attachment=True)

    except Exception as e:
        app.logger.error(f"Failed to create or send EPUB: {e}")
        return "An error occurred during file processing.", 500

if __name__ == "__main__":
    app.run(debug=True)
