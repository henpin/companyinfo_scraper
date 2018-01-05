#! /usr/bin/python
#-*- coding: utf-8 -*-

import re

# Global Patterns 
alphabets = re.compile("[a-zA-Z]+")
alnum = re.compile("[a-zA-Z0-9]+")
rulename = re.compile("[a-zA-Z0-9_]+")
printable = re.compile("\S+")
includeBR = re.compile("^\S[\S\ ]*$")
except_nl = re.compile("[^\\n]+")
post_marked = re.compile("〒[0-9]+[-][0-9]+")
all = re.compile('.*')

dummy = re.compile("")
compiled_reClass = dummy.__class__

def is_compiled_regExpr(obj):
	""" コンパイル済み正規表現オブジェクトであるか否か """
	return isinstance(obj,compiled_reClass)
	
def match_in(text,reList):
    """ テキストとreのリストをとってまっちんぐ """
    return any( pattern.match(text) for pattern in reList )
    
def search_in(text,reList):
    """ テキストとreのリストをとってまっちんぐ """
    for pattern in reList :
        match = pattern.search(text)
        if match :
            return match

