"""Miscellaneous utilities"""

import os

def str_contains_word(s:str,string:str) -> bool:
    d = s.lower().split(" ")
    return string in d

def list_get_maxlen(l:list) -> int:
    return max([len(s) for s in l])

def smart_trim_text(s:str,towhatlength:int) -> str:
    strlen = len(s)
    if strlen <= towhatlength:
        return s
    else:
        #Trimming is needed
        return s[0:towhatlength-4]+"..."
    
def collapse_list(l:list):
    t = []
    for irtem in l:
        if type(irtem) == list:
            t.extend(collapse_list(irtem))#type:ignore
        else:
            t.append(irtem)

    return t


def strict_word_search(haystack:str,needle:str) -> bool:
    #PHP
    words = haystack.split(" ")
    return needle in words