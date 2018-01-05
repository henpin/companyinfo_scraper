# -*- coding: utf-8 -*

import scrapy


"""
Scrapyで使うItem
"""
class URLItem(scrapy.Item):
    """
    URL情報格納リスト
    """
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()


