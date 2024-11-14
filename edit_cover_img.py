# coding=utf-8
import ebooklib
from ebooklib import epub
from datetime import datetime


if __name__ == '__main__':

    ori = epub.read_epub('original.epub')
    ch_list = []

    # get metadata of original book
    li_title = ori.get_metadata('DC', 'title')
    ori_title = li_title[0][0]
    li_author = ori.get_metadata('DC', 'creator')
    ori_author = li_author[0][0]

    # creating new book
    book = epub.EpubBook()

    # calculating identifier for new book
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")

    # add metadata
    book.set_identifier(dt_string)
    book.set_title(ori_title)
    book.set_language('en')
    book.add_author(ori_author)

    # add cover image
    book.set_cover("image.jpg", open('cover.jpg', 'rb').read())

    # intro chapter
    intro = "Blank Page"
    c1 = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='hr')
    c1.content=u'<html><head></head><body><p>'+intro+'</p></body></html>'

    # about chapter
    c2 = epub.EpubHtml(title='Cover Page', file_name='about.xhtml')
    c2.content='<p>Cover Image</p><p><img src="image.jpg" alt="Cover Image"/></p>'

    # add starting two chapters to the book
    book.add_item(c1)
    book.add_item(c2)

    # adding content (both text and imgs) extracted from original book
    i = 1
    for item in ori.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            name = item.get_name()
            ch = epub.EpubHtml(title='Chapter '+str(i), file_name = name[5:])
            ch.content = item.get_content()
            ch_list.append(ch)
            book.add_item(ch)
            i = i + 1

        if item.get_type() == ebooklib.ITEM_IMAGE:
            b_img = item.get_content()
            img_name = item.get_name()
            img_id = item.get_id()
            img_item = epub.EpubItem(uid=img_id, file_name=img_name, media_type='image/jpeg', content=b_img)
            book.add_item(img_item)


    # create table of contents
    # - add manual link
    # - add section
    # - add auto created links to chapters


    book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'), (epub.Section('Contents'), ch_list))

    # add navigation files
    # NOTE: Do not remove navigation, if you do then iBooks shows the epub as corrupt
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())


    # define css style
    style = '''
@namespace epub "http://www.idpf.org/2007/ops";
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}
h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;
}
ol {
        list-style-type: none;
}
ol > li:first-child {
        margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}
'''

    # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # create spin, add cover page as first page
    book.spine = ['cover', 'nav', c1, c2] + ch_list

    # create epub file
    epub.write_epub(ori_title+'_modified'+'.epub', book, {})
