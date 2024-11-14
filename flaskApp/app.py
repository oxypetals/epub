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
    # Your existing file processing logic here...

    @after_this_request
    def cleanup_files(response):
        try:
            # Check and remove the EPUB file if it exists
            if os.path.exists(new_epub_path):
                os.remove(new_epub_path)
            # Check and remove the cover image file if it exists
            if os.path.exists(cover_img_path):
                os.remove(cover_img_path)
            # You might want to check for other files similarly
        except Exception as e:
            app.logger.error(f"Error cleaning up files: {e}")
        return response

        return send_from_directory(directory=UPLOAD_FOLDER, filename=os.path.basename(new_epub_path), as_attachment=True)

    except Exception as e:
        app.logger.error(f"Failed to create or send EPUB: {e}")
        return "An error occurred during file processing.", 500

if __name__ == "__main__":
    app.run(debug=True)
