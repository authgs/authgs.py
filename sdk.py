import AuthGS
import os
import subprocess
import sys

import requests


def get_hardware_id():
    if "nt" in os.name:
        return (
            str(subprocess.check_output("wmic csproduct get uuid"))
            .split("\\r\\n")[1]
            .strip("\\r")
            .strip()
        )
    else:
        return subprocess.Popen("cat /etc/machine-id").split()


class Public:
    def __init__(
        self, app: str = None, user_agent: str = None, host: str = "https://api.auth.gs/app"
    ):
        self.host = host
        self.app = app
        self.user_agent = AuthGS.USER_AGENT if user_agent == None else user_agent

        self.headers = {"App": self.app, "User-Agent": self.user_agent}

    def read_application_information(self):
        return requests.request("GET", self.host, headers=self.headers).json()

    def get_register_link(self):
        return requests.request("GET", self.host + "/register", headers=self.headers).json()

    def login(self, primary: str, password: str, hardware_id: bool = False):
        if hardware_id == True:
            hardware_id = get_hardware_id()
        else:
            hardware_id = None

        # If object['data']['token'] == None, user has to approve the token through 2FA first
        payload = {"primary": primary, "password": password, "hardware": hardware_id}
        r = requests.request(
            "POST", self.host + "/login", headers=self.headers, data=payload
        ).json()

        if r["error"] == False and r["data"]["token"] != None:
            Private.token = r["data"]["token"]


class Private:
    def __init__(
        self,
        app: str = None,
        user_agent: str = None,
        host: str = "https://api.auth.gs/app",
    ):
        self.host = host
        self.app = str(app)
        self.user_agent = AuthGS.USER_AGENT if user_agent == None else user_agent

        # You have to handle login first before settings this token
        #
        # It is recommended to persist this token, ex. in a file & not call it on every request,
        # the user will get rate limited fairly quickly!
        self.token = None

        self.headers = {"App": self.app, "Token": self.token, "User-Agent": self.user_agent}

    def get_app_files(self):
        request = requests.request("GET", self.host + "/files", headers=self.headers).json()
        return request

    def get_user_data(self):
        return requests.request("GET", self.host + "/user", headers=self.headers).json()

    def get_user_notifications(self):
        params = {"offset": 0, "limit": "100", "orderBy": "id.ASC"}
        return requests.request(
            "GET", self.host + "/user/notifications", headers=self.headers, params=params
        ).json()

    def reset_hardware_id(self):
        params = {"offset": 0, "limit": "100", "orderBy": "id.ASC"}
        return requests.request(
            "DELETE", self.host + "/hardware", headers=self.headers, params=params
        ).json()

    def increase_security_flags(self):
        # If token = None, user has to approve the token through 2FA first
        return requests.request(
            "PATCH", self.host + "/increase_security_flags", headers=self.headers
        ).json()

    def redeem_giftcode_or_license(self, code: str = ""):
        params = {"code": code}
        return requests.request(
            "PATCH", self.host + "/redeem", headers=self.headers, params=params
        ).json()
