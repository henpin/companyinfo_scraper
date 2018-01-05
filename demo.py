# -*- coding: utf-8 -*-

from jphrase_parser2 import JPhraseParser
import re_utils


class MyParser(JPhraseParser):
    def __init__(self):
        JPhraseParser.__init__(self)
        self.addRePhrase(u"代表取締役社長|代表取締役")
        self.addRePhrase(u"〒[0-9]+[-][0-9]+")


    def main(self):
        text = u"""
            本社:〒530-0005
            大阪府大阪市北区中之島2丁目2番7号
            中之島セントラルタワー 21階
            TEL：06-4400-8882
            FAX：06-4400-8883
            e-Mail：
            info@isosoken.com
            ■アクセスマップ
        """
        for line in text.split(u"\n"):
            result = self.parse(line,True)
            include_proper = lambda phrase : self.predicate(phrase,
                lambda tok:self.isProperNoun(tok) and not re_utils.rulename.search(tok.surface)
                )
            result = filter( include_proper, result )
            for tok in result :
                print tok
            print ""


if __name__ == '__main__':
    MyParser().main()
