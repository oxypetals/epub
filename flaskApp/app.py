from flask import Flask, request, Response, send_from_directory, render_template, after_this_request
import os
import ebooklib
from ebooklib import epub
from datetime import datetime

app = Flask(__name__)

# Configure upload directory
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Ensure upload folder exists

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

        # Read and process the original EPUB
        ori = epub.read_epub(original_epub)
        ori_title = ori.get_metadata('DC', 'title')[0][0]
        ori_author = ori.get_metadata('DC', 'creator')[0][0]

        # Create new EPUB
        book = epub.EpubBook()
        book.set_identifier(datetime.now().strftime("%Y%m%d%H%M%S"))
        book.set_title(ori_title)
        book.set_language('en')
        book.add_author(ori_author)
        book.set_cover("image.jpg", cover_img.read())

        # Intro chapter
        c1 = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='en')
        c1.content = u'<html><head></head><body><p>Blank Page</p></body></html>'
        book.add_item(c1)

        # About chapter
        c2 = epub.EpubHtml(title='Cover Page', file_name='about.xhtml')
        c2.content = '<p>Cover Image</p><img src="image.jpg" alt="Cover Image"/>'
        book.add_item(c2)

        # Add original content
        ch_list = []
        for item in ori.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                ch = epub.EpubHtml(title='Chapter', file_name=item.get_name()[5:], lang='en')
                ch.content = item.get_content()
                ch_list.append(ch)
                book.add_item(ch)

        book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'), (epub.Section('Contents'), ch_list))
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Save the new EPUB
        file_path = os.path.join(UPLOAD_FOLDER, f"{ori_title}_{book.get_identifier()}.epub")
        epub.write_epub(file_path, book, {})

        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as e:
                app.logger.error(f"Error removing file: {e}")
            return response

        return send_from_directory(directory=UPLOAD_FOLDER, filename=os.path.basename(file_path), as_attachment=True)

    except Exception as e:
        app.logger.error(f"Failed to create or send EPUB: {e}")
        return Response(f"An error occurred: {str(e)}", status=500)

if __name__ == "__main__":
    app.run(debug=True)
