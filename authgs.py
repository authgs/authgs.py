import os
import subprocess
import sys

import requests


def get_hardware_id():
    if 'nt' in os.name:
        return (subprocess.check_output('wmic csproduct get uuid')).split('\\r\\n')[1].strip('\\r').strip()
    else:
        return subprocess.Popen('cat /etc/machine-id'.split())


class Public:
    def __init__(self):
        self.api = "https://api.auth.gs/app"
        self.app = "00000"
        self.userAgent = 'PyApp'

    def read_application_information(self):
        url = self.api + ""
        payload = {}
        headers = {
            'App': self.app,
            'User-Agent': self.userAgent
        }
        return requests.request("GET", url, headers=headers, data=payload).json()

    def get_register_link(self):
        url = self.api + "/register"
        payload = {}
        headers = {
            'App': self.app,
            'User-Agent': self.userAgent
        }
        return requests.request("GET", url, headers=headers, data=payload).json()

    def login(self, primary: str, password: str, hardware_id: bool = None):
        url = self.api + "/login"

        if hardware_id:
            hardware_id = get_hardware_id()
        else:
            hardware_id = None

        payload = {
            'primary': primary,
            'password': password,
            'hardware': hardware_id
        }
        headers = {
            'App': self.app,
            'User-Agent': self.userAgent
        }
        # If object['data']['token'] == None, user has to approve the token through 2FA first
        request = requests.request("POST", url, headers=headers, data=payload).json()
        print('Using token: ' + request['data']['token'])
        if request['error']:
            print('Error: ' + request['message'])
            sys.exit()
        else:
            return request


class Private:
    def __init__(self):
        self.api = "https://api.auth.gs/app"
        self.app = "00000"
        self.userAgent = 'PyApp'

        # You have to handle login first before settings this token
        #
        # It is recommended to persist this token, ex. in a file & not call it on every request,
        # the user will get rate limited fairly quickly!
        fetch = Public().login('username/email', 'password', False)
        self.token = fetch['data']['token']

    def get_app_files(self):
        url = self.api + "/files"
        payload = {}
        headers = {
            'App': self.app,
            'Token': self.token,
            'User-Agent': self.userAgent
        }
        request = requests.request("GET", url, headers=headers, data=payload).json()
        return request

    def get_user_data(self):
        url = self.api + "/user"
        payload = {}
        headers = {
            'App': self.app,
            'Token': self.token,
            'User-Agent': self.userAgent
        }
        return requests.request("GET", url, headers=headers, data=payload).json()

    def get_user_notifications(self):
        url = self.api + "/user/notifications"
        params = {
            'offset': 0,
            'limit': '100',
            'orderBy': 'id.ASC'
        }
        payload = {}
        headers = {
            'App': self.app,
            'Token': self.token,
            'User-Agent': self.userAgent
        }
        return requests.request("GET", url, headers=headers, params=params, data=payload).json()

    def reset_hardware_id(self):
        url = self.api + "/hardware"
        params = {
            'offset': 0,
            'limit': '100',
            'orderBy': 'id.ASC'
        }
        payload = {}
        headers = {
            'App': self.app,
            'Token': self.token,
            'User-Agent': self.userAgent
        }

        return requests.request("DELETE", url, headers=headers, params=params, data=payload).json()

    def increase_security_flags(self):
        url = self.api + "/increase_security_flags"
        headers = {
            'App': self.app,
            'Token': self.token,
            'User-Agent': self.userAgent
        }
        # If token = None, user has to approve the token through 2FA first
        return requests.request("PATCH", url, headers=headers).json()

    def redeem_giftcode_or_license(self, code: str = ''):
        url = self.api + "/redeem"
        params = {
            'code': code
        }
        payload = {}
        headers = {
            'App': self.app,
            'Token': self.token,
            'User-Agent': self.userAgent
        }
        return requests.request("PATCH", url, headers=headers, params=params, data=payload).json()

# print(Public().read_application_information())
# print(Public().get_register_link())
# print(Public().login('email/username', 'password', False))
# print(Private().get_app_files())
# print(Private().get_user_data())
# print(Private().get_user_notifications())
# print(Private().reset_hardware_id())
# print(Private().increase_security_flags())
# print(Private().redeem_giftcode_or_license('code_here'))
