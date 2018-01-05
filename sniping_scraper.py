#! usr/bin/python
#-*- coding: utf-8 -*-

import urllib2
import re
import urlparse

from janome.tokenizer import Tokenizer
from scrapy_item import URLItem
from bs4 import BeautifulSoup


"""
スナイピングすくレイパークラス
"""

class SnipingScraper(object):
    """
    狙ったターゲットを抽出して、URLリストを返す
    """
    def __init__(self):
        self.targets = []
        self.result = []

    def addTarget(self,*args):
        """
        追加
        """
        for arg in args :
            self.targets.append(arg)

    def doScrape(self,_file,base_url):
        """
        スクレイピング実行関数
        """
        # 結果リスト初期化
        urlList = set()

        # Soupの生成
        soup = BeautifulSoup(_file,"lxml")

        # aタグ探す
        for tag in soup.find_all(self.selectTag) :
            url = urlparse.urljoin(base_url,tag.get("href"))
            urlList.add(url)

        return list(urlList)

    def doCrawlWithScraper(self,urlList,scraper):
        """
        クロールしてスクレイピングする
        """
        pass
        #result = []
        #res = request

    def selectTag(self,tag) :
        """
        タグ検索関数
        """
        if ( tag.name == "a" ) :
            text = tag.text.encode("utf-8")
            # テキストが無いならたぶん画像なので、そのaltを読む
            if not tag.text :
                for tag in tag.children :
                    if tag.name == "img" :
                        rext = tag.get("alt")
            # だめやんな
            if not text : return

            # テキスト検索
            if any( text.find(target) > -1 for target in self.targets ) :
                #print text
                return True


class App(object):
    """
    スクレイピングアプリケーションクラス
    """
    # Initialization
    def __init__(self):
        self.init_scraper()
        self.htmls = [
            "nebit.html",
            "iso.html",
            "iso2.html",
            "sagawa.html",
            "yamato.html",
            "hotta.html",
            "taiken.html",
            "usaco.html"
        ]

    def init_scraper(self):
        # スクレイパの生成
        self.scraper = SnipingScraper()
        #self.scraper.addTarget("企業情報", "会社情報", "会社概要")
        self.scraper.addTarget("プライバシーポリシー", "保護方針", "保護ポリシー", "個人情報の取り扱い")

    # main
    def main(self):
        """ main Methods """
        for fileName in self.htmls :
            _file = self.loadHTML(fileName)
            result = self.scraper.doScrape(_file,fileName)
            result = map(lambda _str : unicode(_str).encode("utf-8"),result)

            print "\n\n" +fileName
            print " / ".join(result)
  
    # setup
    def loadHTML(self,url):
        """ htmlファイルの読み込み """
        return open(url) # ファイルオブジェクトの生成


if __name__ == '__main__' :
    App().main()



