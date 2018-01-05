#/usr/bin/python
# -*- coding: utf-8 -*-

import re
from janome_wrapper import JanomeWrapper

import re_utils

"""
日本語連語解析システム
Janome実装

usage : 
    parser = JPhraseParser()
    parser.addPhrase("代表取締役社長") parser.parse("代表取締役社長浅利均") # -> ["代表取締役社長","浅利均"]
"""

class JPhraseParser(JanomeWrapper):
    """
    日本語連語解析クラス
    """
    def __init__(self):
        self.phraseList = list() # 連語リスト
        self.phraseReList = list() # 連語正規表現リスト

    def addPhrase(self,phrase):
        """
        連語を登録する。
        与えられたフレーズに対して形態素解析で最小マッチングして、
        その列パターンをひたすら保存する
        """
        buf = "" # めかぶノード列バッファ
        for tok in self.tokenize(phrase):
            # 普通名詞なら追加
            if self.isNoun(tok,"normal"):
                buf += tok.surface
            else :
                buf and self.phraseList.append(buf)
                buf = ""

            # フレーズリストに追加
            if buf :
                self.phraseList.append(buf)

    def addRePhrase(self,phrase):
        """
        python-reモジュールの仕様により内部ロジックでパターンを(括弧)で囲う必要がある
        そのためのインターフェイス
        """
        # 規約に則らせる
        phrase = "(" +phrase +")"
        # 正規表現化して保存
        pattern = re.compile(phrase)
        self.phraseReList.append(pattern)


    def parse(self,phrase,greedy=False):
        """
        学習情報を使ってマッチングする
        option :
            greedy : 貪欲マッチング
        """
        result = []
        phraseMatched = []
        buf = ''
        phraseMatching = False # フレーズマッチングしているかの判定

        # ノードごとに結合してフレーズリストとマッチング
        for token in self.tokenize(phrase) :
            surface = token.surface
            if not surface.strip() : continue
            if not buf :
                buf = surface

            elif buf +surface in self.phraseList  :
                # フレーズマッチングしたら、そのまま次のノードをリッスン
                buf += surface
                phraseMatching = True

            else :
                # マッチングしないなら結果に追加
                result.append(buf)
                buf = surface # 現在処理中のノードは次の起点になる

                # フレーズマッチングであったならその地点を保存しておく
                if phraseMatching :
                    phraseMatched.append(len(result)-1)
                    phraseMatching = False 

        # 残りを忘れずに
        if buf :
            result.append(buf)
            buf = ''
            # フレーズマッチングであったならその地点を保存しておく
            if phraseMatching :
                phraseMatched.append(result.length-1)


        # 貪欲マッチング
        if greedy :
            old_result = result
            result = []
            # result単位でぶん回し
            for index,surface in enumerate(old_result) :
                if index in phraseMatched :
                    # フレーズマッチしたトークンなら、そこで検索を打ち切る
                    buf and result.append(buf)
                    result.append(surface)
                    buf = ""

                else :
                    token = self.tokenize(surface)[0]
                    if self.isNoun(token) or self.extractClass(token) in (u"接頭詞",u"記号") : # 名詞相当かで評価
                        buf += surface
                    else :
                        # 名詞相当でさえない場合打ち切り
                        buf and result.append(buf)
                        result.append(surface)
                        buf = ""

            # 残りを忘れずに
            if buf :
                result.append(buf)


        # 正規表現まっちんぐに拠る分割
        if self.phraseReList:
            old_result = result
            result = []
            for surface in old_result :
                # 正規表現まっちん具
                match = re_utils.search_in(surface,self.phraseReList)
                if match :
                    # マッチしたら表現で分割されたサーフェスを追加
                    subList = re.split(match.re,surface)
                    result.extend(subList)

                else :
                    result.append(surface) # 普通に追加

        return result



class App(object):
    def main(self):
        parser = JPhraseParser()
        parser.addRePhrase(u"代表取締役社長|代表取締役")
        parser.addRePhrase(u"〒[0-9]+[-][0-9]+")
        result = parser.parse(u"代表取締役社長山口智雄" ,True)

        for tok in result :
            print tok



if __name__ == '__main__' :
    App().main()
