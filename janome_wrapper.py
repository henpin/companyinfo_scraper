#/usr/bin/python
# -*- coding: utf-8 -*-


import janome.tokenizer


"""
Janomeラッピングクラス
適当にインターフェイスを提供する
"""

class JanomeWrapper(object):
    """
    """
    # トークナイザー
    tokenizer = janome.tokenizer.Tokenizer()

    def tokenize(self,expr):
        """ Janomeトークない図 """
        return JanomeWrapper.tokenizer.tokenize(expr)

    def extractClass(self,token):
        """ 第一級品詞を返す """
        return token.part_of_speech.split(",")[0]

    def extractSubClass(self,token):
        """ 第二級品詞 """
        return token.part_of_speech.split(",")[1]

    def isNoun(self,token,option=""):
        """ 名詞判定 """
        # 形態素情報
        class_ = self.extractClass(token)
        sub_class = self.extractSubClass(token)

        # 判定
        optional = ( not option
            or ( option == "normal" and sub_class != u"固有名詞" )
            or ( option == "proper" and sub_class == u"固有名詞" )
            )

        return class_ == u"名詞" and optional

    def isProperNoun(self,token):
        """ 固有名詞判定ショートカット """
        return self.isNoun(token,"proper")
        
    def predicate(self,phrase_orTokList,stateFunc):
        """
        条件を満たすか検出
        """
        if isinstance(phrase_orTokList,unicode):
            tokList = self.tokenize(phrase_orTokList)
        elif isinstance(phrase_orTokList,list):
            tokList = phrase_orTokList
        else :
            raise TypeError("型が違う")

        return any( stateFunc(tok) for tok in tokList )


