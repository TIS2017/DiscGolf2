import requests
from Player import Player
import time
from requests.auth import HTTPBasicAuth
from config import Config

countries = ["AT", "BE", "HR", "CZ", "DK", "EE", "FI", "FR", "DE", "HU", "IS", "IE", "IT", "LV",
             "LT", "LU", "NL", "NO", "PL", "PT", "RS", "SK", "SI", "ES", "SE", "CH", "UA", "GB"]


def getAllPlayers():
    with requests.Session() as s:
        login_data = dict(username=Config.USERNAME, password=Config.PASSWORD, headers={"Content-type": "application/json"})
        result = s.post(Config.url_login, data=login_data)
        session_name = result.json()["session_name"]
        sessid = result.json()["sessid"]
        token = result.json()["token"]

        t = time.time()
        resultList = list()
        for country in countries:
            i = 0
            while True:
                result = s.get("https://api.pdga.com/services/json/players?offset=" + str(
                    i) + "&limit=200&country=" + country + "&rating!=0")
                if "players" in result.json().keys():
                    players = result.json()["players"]
                    i += len(players)
                    for index in range(0, len(players)):
                        p = players[index]
                        resultList.append(
                            Player(p["first_name"], p["last_name"], p["pdga_number"], p["rating"], p["gender"], True))
                else:
                    break
        logout = s.post(Config.url_logout, headers={"Content-type": "application/json",
                                             "Cookie": session_name + "=" + sessid,
                                             "X-CSRF-Token": token})
        return resultList


def getPlayersByIDArray(pids):
    with requests.Session() as s:
        login_data = dict(username=Config.USERNAME, password=Config.PASSWORD, headers={"Content-type": "application/json"})
        result = s.post(Config.url_login, data=login_data)
        session_name = result.json()["session_name"]
        sessid = result.json()["sessid"]
        token = result.json()["token"]

        t = time.time()

        result_players = []
        for pid in pids:
            player = getPlayerByID(pid, s)
            if player is not None:
                result_players.append(player)

        logout = s.post(Config.url_logout, headers={"Content-type": "application/json",
                                             "Cookie": session_name + "=" + sessid,
                                             "X-CSRF-Token": token})
        return result_players


def getPlayerByID(pid, session):
    result = session.get("https://api.pdga.com/services/json/players?pdga_number=" + str(pid))
    if "players" in result.json().keys():
        player = result.json()["players"]
        p = player[0]
        return Player(p["first_name"], p["last_name"], p["pdga_number"], p["rating"], p["gender"])
    else:
        return None


print(len(getAllPlayers()))
