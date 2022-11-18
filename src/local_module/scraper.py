import re
import time
import urllib.parse
from typing import List, Any, Optional
from dataclasses import dataclass, asdict

import requests
from lxml import html
from bs4 import BeautifulSoup


class Request:
    def __init__(self):
        self.res: Any = None
        self.bs: Any = None

    def get(self, url: str):
        self.res = requests.get(url)
        return self.res

    def soup(self):
        self.bs = BeautifulSoup(self.res.text, "lxml")
        return self.bs


class ALL_PRODUCTS(Request):
    URL: str = "https://www.celes-perfume.com/product-category/all/page/{page_num}/"

    def __init__(self):
        super().__init__()
        self.all_products: List[str] = []

    def get_all_products(self) -> List[str]:
        page_num: int = 73
        while True:
            url: str = self.URL.format(page_num=page_num)
            self.get(url)
            bs = self.soup()
            products: Any = bs.select(selector="a.woocommerce-LoopProduct-link")
            for product in products:
                self.all_products.append(product["href"])
            next_page = bs.select(selector="a.next")
            if not next_page:
                break
            page_num += 1
            time.sleep(1)
        return self.all_products


@dataclass
class Field:
    item_name: Optional[str] = None
    brand_name: Optional[str] = None
    rate: Optional[float] = None
    review_cnt: int = 0
    main_fragrances: Optional[str] = None
    top_note: Optional[str] = None
    middle_note: Optional[str] = None
    last_note: Optional[str] = None
    impression: Optional[str] = None
    scene: Optional[str] = None
    season: Optional[str] = None
    url: Optional[str] = None


class PRODUCT_DETAIL(Request):
    def __init__(self, url_list: List[str]):
        super().__init__()
        self.url_list: List[str] = url_list
        self.table: List[dict] = []

    @staticmethod
    def _get_names(bs) -> list:
        title = bs.select_one("h1").text
        return title.split("–")

    @staticmethod
    def _get_rate(bs) -> tuple:
        rate = bs.select_one("div.woocommerce-product-rating > div > span > strong")
        if rate:
            review_cnt = bs.select_one("a.woocommerce-review-link > span.count")
            return float(rate.text), int(review_cnt.text)
        return None, 0

    @staticmethod
    def _get_main_fragrances(bs) -> str:
        mf_list: List[str] = []
        mf_selector: str = "div.woocommerce-product-details__short-description > p:nth-child(3) > a"
        for elm in bs.select(mf_selector):
            mf_str: str = urllib.parse.unquote(elm["href"]).split("/")[-2]
            mf = re.search(r"[a-zA-Z\-]+", mf_str)
            mf_list.append(mf.group())
        return ",".join(mf_list)

    @staticmethod
    def _get_note_description(bs, target) -> str:
        sd_selector: str = ".woocommerce-product-details__short-description"
        short_description: str = bs.select_one(sd_selector).text
        reg: str = r"(?<=香りのノート).+?(?=香りのイメージと印象)"
        extract = re.search(reg, short_description, flags=re.DOTALL)
        lines: list = extract.group().strip().splitlines()
        for next_index, line in enumerate(lines, 1):
            if line in target and target in ("Top", "Middle", "Last"):
                return ",".join(lines[next_index].split("　"))

    def get_detail(self) -> List[dict]:
        for url in self.url_list:
            record = Field(url=url)
            self.get(url)
            bs = self.soup()
            # name
            brand, item = self._get_names(bs)
            record.brand_name = brand.strip()
            record.item_name = item.strip()

            # rate
            rate, review_cnt = self._get_rate(bs)
            record.rate = rate
            record.review_cnt = review_cnt

            # main_fragrances
            mf: str = self._get_main_fragrances(bs)
            record.main_fragrances = mf

            # notes
            top_note = self._get_note_description(bs, "Top")
            middle_note = self._get_note_description(bs, "Middle")
            last_note = self._get_note_description(bs, "Last")

            # TODO: Eat the icecream later
            from icecream import ic
            ic(top_note)
            ic(middle_note)
            ic(last_note)

            # Append to list
            print(record)
            time.sleep(1)
