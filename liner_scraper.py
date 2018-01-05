#! usr/bin/python
#-*- coding: utf-8 -*-


import urllib2
import re

from bs4 import BeautifulSoup
from bs4 import Comment


"""
直行型スクレイパ
"""

class ScrapeTarget(object):
    """
    スクレイピング対象ホルダー
    """
    def __init__(self,headers,target_re):
        """
        ヘッダリストと、対象条件正規表現を引数にとる
        """
        self.headers = headers
        self.target_re = re.compile(target_re)

    def match_header(self,tag):
        """
        タグをとり、ヘッダとしてマッチングするかチェック
        """
        # 変な最適化
        if tag.name == "a" :
            return

        string = tag.string
        # 任意のヘッダにfindマッチングをかける
        if ( string and len(string) <= 12 and any( string.find(header) >-1 for header in self.headers ) ):
            return True

    def match_target(self,tag):
        """
        ターゲットマッチングをする
        """
        string = tag.string
        if ( string and self.target_re.search(string) ) :
            return True


class ListDict(dict):
    """
    リスト格納辞書
    """
    def add(self,key,val):
        """
        追加。もしなければリストの初期化
        """
        # 文字コードがバグルのでutf-8二変換
        key = unicode(key).encode("utf-8").strip()
        val = unicode(val).encode("utf-8").strip()
        # 保存
        if ( key in self ):
            # 無ければ追加
            ( val not in self.get(key) ) and self.get(key).append(val)
        else :
            self[key] = [val]




class LinerScraper(object):
    """
    直線型スクレイパークラス
    """
    def __init__(self):
        self.targets = []
        self.result = ListDict()

    def addTarget(self,*args):
        """
        スクレイピング対象を追加
        """
        for target in args :
            if not isinstance(target, ScrapeTarget):
                raise TypeError
            else :
                self.targets.append(target)

    def doScrape(self,_file):
        """
        スクレイピング実行関数
        """
        # 結果リスト初期化
        self.result = ListDict()

        # Soupの生成
        soup = BeautifulSoup(_file,"lxml"); 

        # 対象ターゲットごとにぶん回し
        for target in self.targets :
            # ヘッダにマッチングするタグでぶん回し
            for tag in soup.body.find_all( lambda tag : tag.string and target.match_header(tag) ) :
                self.process_headerTag(tag,target)

        return self.result


    def process_headerTag(self,tag,target):
        """
        検知されたヘッダタグの処理
        """
        base_str = tag.string
        _super = tag.parent.parent

        # ヘッダと同レベルに内容があるパターンもあるので処理
        if ( tag.name == "p" and base_str.find(u"　") >-1 ) :
            stripped = base_str.split(u"　")
            before = stripped[0]
            after = stripped[1]
            self.result.add(before,after)
            return

        # 直近15DOMElement以内で検出
        for _ in range(20) :
            tag = tag.next_element
            # コメントならパス
            if isinstance(tag,Comment) : continue
            # 検索中のタグが親の親でないなら終端
            elif ( tag.name and tag not in _super.find_all(tag.name) ) :
                return
            # インライン相当タグでないなら終端
            elif ( tag.name and tag.name not in ("span","br","dd","td","strong","p","a") ):
                return
            # 検索にマッチすれば追加
            string = tag.string
            if string != base_str and target.match_target(tag) :
                self.result.add(base_str,string)
                


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
        # スクレイピング対象リスト
        self.targets = [
            ScrapeTarget([u"本社",u"所在地"] , r"\S"),
            ScrapeTarget([u"代表"] , r"\S"),
            ScrapeTarget([u"事業内容"] , r"\S"),
            ScrapeTarget([u"事業所",u"オフィス",u"支社"] , r"\S"),
            ScrapeTarget([u"従業員数"] , r"[0-9]+")
        ] 

        # スクレイパの生成
        self.scraper = LinerScraper()
        self.scraper.addTarget( *self.targets );

            
    # main
    def main(self):
        """ main Methods """
        for fileName in self.htmls :
            _file = self.loadHTML(fileName)
            result = self.scraper.doScrape(_file)

            print "\n\n" +fileName
            for key,val in result.dict.items() :
                print key +": " +"\n\t".join(val) +"\n--------------------\n"

  
    # setup
    def loadHTML(self,url):
        """ htmlファイルの読み込み """
        return open(url) # ファイルオブジェクトの生成



# 初期化処理
if __name__ == '__main__' :
    App().main()



