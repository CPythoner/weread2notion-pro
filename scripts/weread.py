import os
import argparse
from weread_api import WeReadApi
from notion_helper import NotionHelper

def get_number(number):
    return {"number": number}

def get_heading(level, title):
    return {
        "object": "block",
        "type": "heading_{}".format(level),
        "heading_{}".format(level): {"text": [{"type": "text", "text": {"content": title}}]},
    }

def get_quote(abstract):
    return {
        "object": "block",
        "type": "quote",
        "quote": {"text": [{"type": "text", "text": {"content": abstract}}]},
    }

def get_bookmark_list(page_id, book_id):
    weread_api = WeReadApi()
    bookmark_list = weread_api.get_chapter_info(book_id)
    read_info = weread_api.get_read_info(book_id)
    if read_info:
        bookmark_list.append(read_info)
    return bookmark_list

def get_review_list(page_id, book_id):
    weread_api = WeReadApi()
    reviews = weread_api.get_review_list(book_id)
    return reviews

def sort_notes(page_id, chapter, bookmark_list):
    content = []
    for index, bookmark in enumerate(bookmark_list):
        if bookmark.get("markText"):
            content.append(get_heading(index + 1, bookmark.get("markText")))
        elif bookmark.get("content"):
            content.append(get_heading(index + 1, bookmark.get("content")))
    return content

def append_blocks(id, content):
    blocks = []
    for c in content:
        blocks.append(c)
    return blocks

def append_blocks_to_notion(id, blocks, after, contents):
    response = notion_helper.append_blocks_after(
        block_id=id, children=blocks, after=after
    )
    results = response.get("results")
    l = []
    for index, content in enumerate(contents):
        result = results[index]
        if content.get("abstract") != None and content.get("abstract") != "":
            notion_helper.append_blocks(
                block_id=result.get("id"), children=[get_quote(content.get("abstract"))]
            )
        content["blockId"] = result.get("id")
        l.append(content)
    return l

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    options = parser.parse_args()
    branch = os.getenv("REF").split("/")[-1]
    repository = os.getenv("REPOSITORY")
    cookies = WeReadApi.get_cookies()
    notion_helper = NotionHelper()

    for cookie in cookies:
        weread_api = WeReadApi(cookie)
        notion_books = notion_helper.get_all_book()
        books = weread_api.get_notebooklist()
        print(len(books))
        if books != None:
            for index, book in enumerate(books):
                bookId = book.get("bookId")
                title = book.get("book").get("title")
                sort = book.get("sort")
                if bookId not in notion_books:
                    continue
                if sort == notion_books.get(bookId).get("Sort"):
                    continue
                pageId = notion_books.get(book
