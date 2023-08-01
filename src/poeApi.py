from confighandler import config as cfg
from auth import token
import requests

API_URL = cfg.loadConfig()["api"]

def getCharacters():
    newToken = token.get_token()
    headers = {
        "Authorization": f"Bearer {newToken.accessToken}",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'
    }
    response = requests.request("GET", f"{API_URL}/character", headers=headers)
    if not response.ok:
        return None
    return response.json()

def getStashTabsList(league):
    newToken = token.get_token()
    headers = {
        "Authorization": f"Bearer {newToken.accessToken}",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'
    }
    response = requests.request("GET", f"{API_URL}/stash/{league}", headers=headers)
    if not response.ok:
        return None
    return response.json()

def getStashTab(league, id):
    newToken = token.get_token()
    headers = {
        "Authorization": f"Bearer {newToken.accessToken}",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'
    }
    response = requests.request("GET", f"{API_URL}/stash/{league}/{id}", headers=headers)
    if not response.ok:
        return None
    return response.json()