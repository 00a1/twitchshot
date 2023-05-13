#get screenshot from twitch quick and dirty 5/13/23 3:22am

# -------------------------------------------------------------------
#                   twitchshot :                              Total
#                  Editor time :                             54 min
#             Active code time :                             28 min
#          Lines of code added :                                423
#        Lines of code deleted :                                265
#             Total keystrokes :                                787
# -------------------------------------------------------------------

import enum
import time
import requests
import cv2
import threading
from twitchrealtimehandler import TwitchImageGrabber

Flag = False

class TwitchResponseStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4

class Twitch:
    def __init__(self, Flag):
        self.Flag = Flag
        self.refresh = 15
        self.username = ""
        self.client_id = "client_id"# https://dev.twitch.tv/console/apps
        self.client_secret = "client_secret"# https://dev.twitch.tv/console/apps
        self.token_url = "https://id.twitch.tv/oauth2/token?client_id=" + self.client_id + "&client_secret=" + self.client_secret + "&grant_type=client_credentials"
        self.url = "https://api.twitch.tv/helix/streams"
        self.access_token = self.fetch_access_token()

    def fetch_access_token(self):
        token_response = requests.post(self.token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()
        return token["access_token"]

    def check_user(self):
        info = None
        status = TwitchResponseStatus.ERROR
        try:
            headers = {"Client-ID": self.client_id, "Authorization": "Bearer " + self.access_token}
            r = requests.get(self.url + "?user_login=" + self.username, headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchResponseStatus.OFFLINE
            else:
                status = TwitchResponseStatus.ONLINE
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResponseStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchResponseStatus.NOT_FOUND
        return status, info

    def loop_check(self):
        while True:
            status, _ = self.check_user()
            if status == TwitchResponseStatus.NOT_FOUND:
                print("username not found, invalid username or typo")
                self.Flag = False
                time.sleep(self.refresh)
            elif status == TwitchResponseStatus.ERROR:
                print("unexpected error. will try again in 5 minutes")
                self.Flag = False
                time.sleep(300)
            elif status == TwitchResponseStatus.OFFLINE:
                print(f"currently offline, checking again in {self.refresh} seconds")
                self.Flag = False
                time.sleep(self.refresh)
            elif status == TwitchResponseStatus.UNAUTHORIZED:
                print("unauthorized, will attempt to log back in immediately")
                self.Flag = False
                self.access_token = self.fetch_access_token()
            elif status == TwitchResponseStatus.ONLINE:
                print("online")
                self.Flag = True
                time.sleep(30)

if __name__ == "__main__":
    twitch = Twitch(Flag)
    twitch.username = "vedal987"
    threading.Thread(target=twitch.loop_check, daemon=True).start()
    fps = 5# ads 5 frames to buffer
    while True:
        if twitch.Flag == True:
            img_grabber = TwitchImageGrabber(twitch_url=f"twitch.tv/{twitch.username}", quality="480p", rate=fps, blocking=True)#1080p60 or 1080p
            while twitch.Flag:
                img = img_grabber.grab()
                if img is not None:
                    cv2.imshow("frame", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
            cv2.destroyAllWindows()
            img_grabber.terminate()
    