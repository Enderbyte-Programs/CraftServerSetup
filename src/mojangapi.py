"""Mojang related queries"""
import requests
import uuid

def get_player_uuid(lastusername:str) -> uuid.UUID:
    lnk = "https://api.mojang.com/users/profiles/minecraft/"
    rq = requests.get(lnk+lastusername).json()
    return uuid.UUID(hex=rq["id"])

def get_player_name(uuid:str):
    uuid = uuid.replace("-","")
    lnk = "https://api.minecraftservices.com/minecraft/profile/lookup/"
    rq = requests.get(lnk+uuid).json()
    return rq["name"]