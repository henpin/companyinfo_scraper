# -*- coding: utf-8 -*

from time import sleep
from selenium import webdriver

"""
外部のヘッダレスブラウザを呼ぶので
メモリリークのリスクがあるらしいので局所化
"""

def load_fromSelenium(url):
    """
    セレニアムを使ってJS読み込み後のHTMLを取得
    メモリリークが怖いのでここで開いてここで閉じる
    """
    # PhantomJSによるドライバの初期化
    driver = webdriver.PhantomJS()
    # URL読み込み
    driver.get(url)
    sleep(5) # JS読み込み待ち
    # bodyの取得
    body = driver.find_element_by_tag_name("body")
    # HTMLの取得
    text = body.get_attribute('innerHTML')
    driver.close() # ドライバクローズ
    return text


