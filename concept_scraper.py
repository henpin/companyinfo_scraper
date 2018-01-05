#! usr/bin/python
#-*- coding: utf-8 -*-


import urllib2
import re

from janome.tokenizer import Tokenizer
from bs4 import BeautifulSoup
from bs4 import Comment


"""
HTMLから(気合で)コンセプトを抽出する
"""

class ConceptScraper(object):
    """
    コンセプトスクレイパ
    """
    def __init__(self):
        self.targets = []
        # Janomeトークナイザ生成
        #self.jTokenizer = Tokenizer()

    def doScrape(self,_file):
        """
        スクレイピング実行関数
        Hタグを探すだけという超絶シンプル設計 (ISO総研サイト用)
        """
        # 結果リスト初期化
        concepts = []

        # Soupの生成
        soup = BeautifulSoup(_file,"lxml")

        # Hタグ探す
        for selector in ["h4","h3","h2","h1"] : # 昇順で優先付けできるようにする
            for tag in soup.select(selector):
                text = unicode(tag.text).encode("utf-8")
                concepts.append(text) # テキスト取得

        return concepts



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
        self.scraper = ConceptScraper()

            
    # main
    def main(self):
        """ main Methods """
        for fileName in self.htmls :
            _file = self.loadHTML(fileName)
            result = self.scraper.doScrape(_file)

            print "\n\n" +fileName
            print " / ".join(result)
  
    # setup
    def loadHTML(self,url):
        """ htmlファイルの読み込み """
        return open(url) # ファイルオブジェクトの生成


if __name__ == '__main__':
    App().main()


