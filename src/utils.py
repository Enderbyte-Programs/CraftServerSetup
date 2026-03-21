"""Miscellaneous utilities"""

import datetime

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

def parse_size(data: int) -> str:
    result:str = ""
    if data < 0:
        neg = True
        data = -data
    else:
        neg = False
    if data < 2000:
        result = f"{data} bytes"
    elif data > 2000000000:
        result = f"{round(data/1000000000,2)} GB"
    elif data > 2000000:
        result = f"{round(data/1000000,2)} MB"
    elif data > 2000:
        result = f"{round(data/1000,2)} KB"
    if neg:
        result = "-"+result
    return result

def strip_datetime(d:datetime.datetime) -> str:
    return d.strftime("%Y-%m-%d %H:%M:%S")

def count_unique_values(l:list) -> int:
    return len(set(l))

def remove_duplicates_from_list(l:list) -> list:
    return list(set(l))

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

def friendly_positions(ins:int) -> str:
    conv = str(ins)
    if conv.endswith("1"):
        conv += "st"
    elif conv.endswith("2"):
        conv += "nd"
    elif conv.endswith("3"):
        conv += "rd"
    else:
        conv += "th"
    return conv

def split_list_into_chunks(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]
        
def sort_dict_by_key(d:dict) -> dict:
    return dict(sorted(list(d.items())))

def average_list(l:list[int|float]) -> float:
    return sum(l)/len(l)
            
def recursive_average(l:list[list[int|float]]) -> list[float]:
    return [average_list(z) for z in l]