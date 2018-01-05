#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
import json

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
import google

from bs4 import BeautifulSoup
from scrapy_item import URLItem
from liner_scraper import LinerScraper
from liner_scraper import ScrapeTarget,ListDict
from concept_scraper import ConceptScraper
from sniping_scraper import SnipingScraper
import selenium_loader


"""
会社情報クローラ
"""
COMPANYINFO_PHRASE = [ "企業情報", "会社情報", "会社概要", "会社案内", "企業概要" ]
POLICY_PHRASE = [ "プライバシーポリシー", "保護方針", "保護ポリシー", "個人情報の取り扱い" ]

def is_companyInfoUrl(urlItem):
    """
    会社情報HMLTか判定
    """
    # HTML情報
    title = urlItem["title"]
    body = urlItem["text"]

    # 名前で判定
    companyInfoPhrase = COMPANYINFO_PHRASE
    if any( title.find(phrase) > -1 for phrase in companyInfoPhrase ):
        return True

    # コンセプトで判定
    concepts = ConceptScraper().doScrape(body)
    if any( ( phrase in concepts ) for phrase in companyInfoPhrase ):
        return True


def is_policyURL(urlItem):
    """
    プライバシーポリシーのURLを見つける
    """
    # HTML情報
    title = urlItem["title"]
    body = urlItem["text"]
    # 名前で判定
    policyPhrase = POLICY_PHRASE
    if any( title.find(phrase) > -1 for phrase in policyPhrase ):
        return True
    # コンセプトで判定
    concepts = ConceptScraper().doScrape(body)
    if any( any( concept.find(phrase) > -1 for concept in concepts ) for phrase in policyPhrase ):
        return True



def gen_spider(url,dataList,process_value,snipingScraper) :
    """
    やりたくないけどスパイダ動的生成
    """
    class URLSpider(CrawlSpider):
        """
        URLおよびタイトル補足スパイダー
        """
        name = "url"
        # URL設定
        allow_domains = [url]
        start_urls = [url]
        # クローリングルール
        rules = [
            Rule(LinkExtractor(process_value=process_value), callback='parse_url', follow=True)
            ]
            
        def parse_url(self,response):
            """
            パーシング
            """
            item = URLItem()
            # URL,title,bodyの取得
            item["url"] = response.url
            item["title"] = response.css("title").xpath('string()').extract_first().encode("utf-8")
            # topページだけseleniumでJS処理
            if ( URLSpider.start_urls[0] == item["url"] ) :
                item["text"] = selenium_loader.load_fromSelenium(item["url"])
            else :
                item["text"] = response.body
            # 保存
            dataList.append(item)

            # 企業案内ならパース
            if is_companyInfoUrl(item) :
                result = CompanyInfoScraper().doScrape(response.body) # 企業情報スクレイパでスクレイピング
                dataList.append(result) # 保存

            # スナイピング
            urlList = snipingScraper.doScrape(item["text"],item["url"])
            for url in map(lambda url : process_value(url,force=True),urlList) :
                if (url) :
                    #print url
                    yield scrapy.Request(url,self.parse_url,priority=1000,dont_filter=True)


    # スパイダの返却
    return URLSpider



class CompanyInfoScraper(LinerScraper):
    """
    企業情報補足スクレイパ
    """
    def __init__(self):
        super(CompanyInfoScraper,self).__init__()
        # スクレイピング対象リスト
        targets = [
            ScrapeTarget([u"本社",u"所在地"] , r"\S"),
            ScrapeTarget([u"代表"] , r"\S"),
            ScrapeTarget([u"事業内容"] , r"\S"),
            ScrapeTarget([u"事業所",u"オフィス",u"支社"] , r"\S"),
            ScrapeTarget([u"従業員数"] , r"[0-9]+")
        ] 
        # 追加
        self.addTarget( *targets )



class App(object):
    """ アプリケーションクラス """
    def __init__(self):
        self.dataList = []
        self.urlList = []
        self.domain_re = re.compile(r"(?:https?|ftps?)://([A-Za-z0-9-]{1,63}\.)*(?:(com)|(org)|([A-Za-z0-9-]{1,63}\.)([A-Za-z0-9-]{1,63}))/?[A-Za-z0-9.\-?=#%/]*")
        self.target_domain = ""
        self.crawlLimit = 50
        # 設定済みクローラ定義
        self.crawlSettings = {
            'BOT_NAME' : 'nebit_bot',
            'FEED_EXPORT_ENCODING' : 'utf-8',
            'ROBOTSTXT_OBEY' : True,
            'DOWNLOAD_DELAY' : 2, #１秒ディレイ
            #'DEPTH_LIMIT' : 2, #深さ2
            #'DEPTH_PRIORITY' : 1, #幅優先探索
        }

        companyInfoPhrase = COMPANYINFO_PHRASE
        policyPhrase = POLICY_PHRASE
        # スナイピングスクレイパ
        self.snipingScraper = SnipingScraper()
        self.snipingScraper.addTarget( *companyInfoPhrase )
        self.snipingScraper.addTarget( *policyPhrase )


    def extract_domain(self,url):
        """
        URLからドメイン名を抜き取る
        """
        m = self.domain_re.match(url)
        if m:
            return ("".join(map(str, m.groups(''))))

    def find_url(self,name):
        """
        Google検索でURL取得
        """
        url = google.search(name,lang="ja",stop=1)
        return list(url)[0]

    def filter_url(self,value,force=False):
        """
        URLのフィルタリング
        """
        # ドメイン名でフィルタリング
        domain = self.extract_domain(value)
        if domain and domain != self.target_domain :
            return
            
        # 重複チェック
        if (value in self.urlList):
            return None
        elif force : # 強制検索
            self.urlList.append(value)
            return value
        elif len(self.urlList) > self.crawlLimit : # ページ限度数
            return 
        else :
            self.urlList.append(value)
            return value


    def doCrawl(self,url):
        """
        クローリングする
        """
        # ドメイン名設定
        self.target_domain = self.extract_domain(url)

        # プロセスとスパイダーの生成
        process = CrawlerProcess(self.crawlSettings)
        spider = gen_spider(url,self.dataList,self.filter_url,self.snipingScraper)

        # クローリングセットアップ
        process.crawl(spider)
        # クローリング
        process.start()

    def convert2JSON(self):
        """ JSONへの変換関数 """
        # まんまJSON
        jsonDict = dict() 
        jsonDict["url"] = []
        jsonDict["policy_url"] = []

        # 値の抽出
        for data in self.dataList:
            # ItemならURL抽出
            if isinstance(data,URLItem) :
                if is_policyURL(data):
                    jsonDict["policy_url"].append(data["url"])
                jsonDict["url"].append(data["url"])
                continue

            # 会社情報抽出
            for key,value in data.items():
                value = "\n".join(value)
                # 代表社名探し
                if key.find("代表") > -1:
                    jsonDict["代表者名"] = value
                    jsonDict["代表者役職名"] = key

                # 本社探し
                elif re.search(r"本社|所在地",key):
                    jsonDict["本社"] = value
                
                # 事業案内
                elif key.find("事業内容") > -1:
                    if jsonDict.get("事業内容") :
                        jsonDict["事業内容"].append(value)
                    else :
                        jsonDict["事業内容"] = [value]

                # 事業所
                elif re.search(r"事業所|オフィス|支社",key):
                    jsonDict[key] = [value]
                        
                # 従業員数
                elif key.find("従業員数") > -1:
                    jsonDict["従業員数"] = value

        # debug print
        for key,val in jsonDict.items():
            if isinstance(val,list):
                val = ", ".join(val)
            print key +":" +val

        return json.dumps(jsonDict)

        
    def debug_print(self):
        """ デバッグプリント """
        # 会社名
        print "\n\n %s \n" % (company_name,)

        # アイテムのほうのリスト
        allItems = filter(lambda data : not isinstance(data,ListDict),self.dataList)

        # プライバシーポリシーURLを見つける
        Pitems = filter( is_policyURL, allItems )
        for item in Pitems :
            print "ポリシーURL : %s \n--------------------\n" % (item["url"],)

        # とりあえずフォームのあるページを見てみる
        for item in allItems :
            if ( item["url"].startswith("https") ) :
                soup = BeautifulSoup(item["text"],"lxml")
                if ( soup.find_all(lambda tag : tag.name == "input" and tag.get("type") == "submit") ) :
                    print "個人情報入力URL : %s \n--------------------\n" %(item["url"])

        # 結果を出力
        for item in filter(lambda data : isinstance(data,ListDict),self.dataList):
            if ( isinstance(item,ListDict) ) :
                for key, val in item.dict.items() :
                    print key +": " +"\n\t".join(val) +"\n--------------------\n"

        for item in allItems :
            print item.get("url") +":\t\t" +item.get("title")


    def main(self):
        """ エントリーポイント"""
        company_name = "ISO総合研究所"
        # Googleから会社名の取得
        url = self.find_url(company_name)
        # クローリング
        self.doCrawl(url)

        #self.debug_print()
        print self.convert2JSON()


if __name__ == '__main__' :
    App().main()

