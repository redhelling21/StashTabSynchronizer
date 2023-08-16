from confighandler import config as cfg
from auth import token
import requests
from logger import appLogger
import time

API_URL = cfg.loadConfig()["api"]


class POEApi:
    _instance = None

    def RateLimited(func):
        def wrapper(self, *args, **kwargs):
            if self.maxWaitingNeeded > 0:
                appLogger.info(f"Detected the need of a temporisation. Waiting {self.maxWaitingNeeded}s")
                time.sleep(self.maxWaitingNeeded)
            elif self.mostCloseToBreakingRule[0] < 2:
                appLogger.info(f"The rate limit is near. Waiting {self.mostCloseToBreakingRule[1]}s to avoid it.")
                time.sleep(self.mostCloseToBreakingRule[1])
            result = func(self, *args, **kwargs)
            resHeaders = result.headers
            if result.status_code == 429:
                retryAfter = resHeaders["retry-after"]
                appLogger.debug(f"Rate limiting detected. Waiting {retryAfter+10}s")
                time.sleep(retryAfter + 10)
                return func(self, *args, **kwargs)
            elif not result.ok:
                return None
            if resHeaders.get("X-Rate-Limit-Rules") is not None:
                rules = resHeaders["X-Rate-Limit-Rules"].split(",")
                self.maxWaitingNeeded = 0
                self.mostCloseToBreakingRule = (999, 0)
                for rule in rules:
                    subrules = resHeaders.get(f"X-Rate-Limit-{rule}", "").split(",")
                    substates = resHeaders.get(f"X-Rate-Limit-{rule}-State", "").split(",")
                    for i in range(len(subrules)):
                        subsubrule = subrules[i].split(":")
                        subsubstate = substates[i].split(":")
                        if self.maxWaitingNeeded < int(subsubstate[2]):
                            self.maxWaitingNeeded = int(subsubstate[2])
                        if self.mostCloseToBreakingRule[0] > (int(subsubrule[0]) - int(subsubstate[0])):
                            self.mostCloseToBreakingRule = (
                                int(subsubrule[0]) - int(subsubstate[0]),
                                int(subsubrule[1]),
                            )
            return result.json()

        return wrapper

    def PoeApiRequest(func):
        def wrapper(self, *args, **kwargs):
            newToken = token.get_token()
            headers = {
                "Authorization": f"Bearer {newToken.accessToken}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
            }
            result = func(self, headers, *args, **kwargs)
            if not result.ok:
                appLogger.error(f"Could not send to {result.url} with headers {headers}: {result.status_code}")
            return result

        return wrapper

    def __init_once(self):
        conf = cfg.loadConfig()
        if conf is not None and "api" in conf:
            self.url = conf["api"]
            appLogger.info("Loaded api url from config : %s", str(self.url))
        else:
            self.url = None
        self.maxWaitingNeeded = 0
        self.mostCloseToBreakingRule = (999, 0)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(POEApi, cls).__new__(cls)
            cls._instance.__init_once()
        return cls._instance

    @RateLimited
    @PoeApiRequest
    def getCharacters(self, headers):
        return requests.request("GET", f"{API_URL}/character", headers=headers)

    @RateLimited
    @PoeApiRequest
    def getStashTabsList(self, headers, league):
        return requests.request("GET", f"{API_URL}/stash/{league}", headers=headers)

    @RateLimited
    @PoeApiRequest
    def getStashTab(self, headers, league, id):
        return requests.request("GET", f"{API_URL}/stash/{league}/{id}", headers=headers)

    @RateLimited
    @PoeApiRequest
    def getProfile(self, headers):
        return requests.request("GET", f"{API_URL}/profile", headers=headers)
