import requests
import hashlib
import random

class ProductKey:
    def __init__(self,s:str):
        self.s = s
        self.hex = hashlib.sha512(s.encode()).hexdigest()

def generate_product_key() -> ProductKey:
    khz = list("1234567890abcdefghijklmnopqrstuvwxyz")
    final = ""
    for i in range(16):
        final += random.choice(khz)
    return ProductKey(final)

DATA = []
def load_data(url:str):
    global DATA
    DATA = requests.get(url).text.splitlines()

def check(inputs:str) -> bool:
    return hashlib.sha512(inputs.encode()).hexdigest() in DATA
