from flask import Flask, request, send_from_directory, render_template, after_this_request
import os
from ebooklib import epub
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Ensure the upload folder exists

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

        # Save the uploaded files temporarily
        cover_img_path = os.path.join(UPLOAD_FOLDER, cover_img.filename)
        original_epub_path = os.path.join(UPLOAD_FOLDER, original_epub.filename)
        cover_img.save(cover_img_path)
        original_epub.save(original_epub_path)

        # Process the EPUB
        ori = epub.read_epub(original_epub_path)  # Use the saved file path
        book = epub.EpubBook()
        book.set_identifier(datetime.now().strftime("%Y%m%d%H%M%S"))
        book.set_title('New Title')  # Example, you should extract this from ori if needed
        book.set_language('en')
        book.add_author('Author Name')  # Example, you should extract this from ori if needed

        # Set and read the cover image
        with open(cover_img_path, 'rb') as img_file:
            book.set_cover("image.jpg", img_file.read())

        # Save the new EPUB
        new_epub_path = os.path.join(UPLOAD_FOLDER, f"modified_{datetime.now().strftime('%Y%m%d%H%M%S')}.epub")
        epub.write_epub(new_epub_path, book, {})

        @after_this_request
        def remove_files(response):
            try:
                os.remove(cover_img_path)
                os.remove(original_epub_path)
                os.remove(new_epub_path)
            except Exception as e:
                app.logger.error(f"Error removing files: {e}")
            return response

        return send_from_directory(directory=UPLOAD_FOLDER, filename=os.path.basename(new_epub_path), as_attachment=True)

    except Exception as e:
        app.logger.error(f"Failed to create or send EPUB: {e}")
        return "An error occurred during file processing.", 500

if __name__ == "__main__":
    app.run(debug=True)
