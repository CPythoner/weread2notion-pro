import hashlib
from http.cookies import SimpleCookie
import os
import re
import requests
from requests.utils import cookiejar_from_dict
from retrying import retry

WEREAD_URL = "https://weread.qq.com/"
WEREAD_NOTEBOOKS_URL = "https://i.weread.qq.com/user/notebooks"
WEREAD_BOOKMARKLIST_URL = "https://i.weread.qq.com/book/bookmarklist"
WEREAD_CHAPTER_INFO = "https://i.weread.qq.com/book/chapterInfos"
WEREAD_READ_INFO_URL = "https://i.weread.qq.com/book/readinfo"
WEREAD_REVIEW_LIST_URL = "https://i.weread.qq.com/review/list"
WEREAD_BOOK_INFO = "https://i.weread.qq.com/book/info"
WEREAD_READDATA_DETAIL = "https://i.weread.qq.com/readdata/detail"
WEREAD_HISTORY_URL = "https://i.weread.qq.com/readdata/summary?synckey=0"


class WeReadApi:
    def __init__(self, cookie):
        self.cookie = cookie
        self.session = requests.Session()
        self.session.cookies = self.parse_cookie_string(cookie)

    def try_get_cloud_cookie(self, url, id, password):
        if url.endswith("/"):
            url = url[:-1]
        req_url = f"{url}/get/{id}"
        data = {"password": password}
        result = None
        response = requests.post(req_url, data=data)
        if response.status_code == 200:
            data = response.json()
            cookie_data = data.get("cookie_data")
            if cookie_data and "weread.qq.com" in cookie_data:
                cookies = cookie_data["weread.qq.com"]
                cookie_str = "; ".join(
                    [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
                )
                result = cookie_str
        return result

    @staticmethod
    def get_cookies():
        url = os.getenv("CC_URL")
        if not url:
            url = "https://cookiecloud.malinkang.com/"
        id = os.getenv("CC_ID")
        password = os.getenv("CC_PASSWORD")
        cookie = os.getenv("WEREAD_COOKIE")
        if url and id and password:
            cookie = self.try_get_cloud_cookie(url, id, password)
        return cookie.split("|")

    @staticmethod
    def parse_cookie_string(cookie_str):
        cookie = SimpleCookie()
        cookie.load(cookie_str)
        cookies = {key: morsel.value for key, morsel in cookie.items()}
        return cookiejar_from_dict(cookies)

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_notebooklist(self):
        response = self.session.get(WEREAD_NOTEBOOKS_URL)
        if response.status_code == 200:
            return response.json().get("books", [])
        return None

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_chapter_info(self, book_id):
        response = self.session.get(WEREAD_CHAPTER_INFO, params={"bookIds": book_id})
        if response.status_code == 200:
            return response.json().get("data", {}).get(book_id, [])
        return None

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_read_info(self, book_id):
        response = self.session.get(WEREAD_READ_INFO_URL, params={"bookId": book_id})
        if response.status_code == 200:
            return response.json().get("readInfo", {})
        return None

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_review_list(self, book_id):
        response = self.session.get(WEREAD_REVIEW_LIST_URL, params={"bookId": book_id})
        if response.status_code == 200:
            return response.json().get("reviews", [])
        return None

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_book_info(self, book_id):
        response = self.session.get(WEREAD_BOOK_INFO, params={"bookId": book_id})
        if response.status_code == 200:
            return response.json().get("bookInfo", {})
        return None

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_read_data_detail(self, book_id):
        response = self.session.get(WEREAD_READDATA_DETAIL, params={"bookId": book_id})
        if response.status_code == 200:
            return response.json().get("readDataDetail", {})
        return None

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_history(self):
        response = self.session.get(WEREAD_HISTORY_URL)
        if response.status_code == 200:
            return response.json().get("history", [])
        return None
