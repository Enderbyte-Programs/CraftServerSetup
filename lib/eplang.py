"""EPLANG: The Enderbyte Programs Language library

This library uses a java-like dictionary to store strings for your program.
"""

import os
import json

class LanguageFile:
    def __init__(self,filepath):
        self.path = filepath
        self.language = None
        with open(filepath) as f:
            self.raw = json.load(f)
        self.data = None
    def get_available_languages_raw(self):
        """Get a list of languages this file supports by their internal name (like en-CA or fr-FR)"""
        return list(self.raw["available"].keys())
    def get_available_languages_dict(self):
        """Get a list of available languages in a dict with format name:friendly name"""
        return self.raw["available"]
    def get_available_languages_friendly(self):
        """Get a list of languages by their friendly user name (like English or Francais)"""
        return list(self.raw["available"].values())
    def set_active_language(self,language):
        """Set active language. language must be an interenal name (like en-CA) and **NOT** a friendly name
        Calling this function will also load data to improve performance"""
        self.language = language
        self.data = self.get_language_dict()
    def get_language_dict(self):
        """Get a dictionary of all strings in the set language, with structure {code:data}"""
        final = {}
        for item in self.raw["strings"].items():
            fk = item[0]
            fa = fk
            fi = 0
            for translation in list(item[1].keys()):
                if self.language in translation.split(";"):
                    fa = list(item[1].values())[fi]
                fi += 1
            final[fk] = fa
        return final
    def get(self,code) -> str:
        return self.data[code]
    
if __name__ == "__main__":
    f = LanguageFile("langfile.json")
    f.set_active_language("en-CA")
    d = f.get_language_dict()
    print(d)