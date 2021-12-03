import requests
from controller.utils import random_str
import json


BASE_URL = 'http://localhost:8080'
AUTH_HEADER = 'x-authorization'

CREATE_ACCOUNT = '/auth/create-account'
DELETE_ACCOUNT = '/auth/delete'
LOGIN = '/auth/login'


class Requests():
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.auth_header = None

    def test_connection(self):
        url = self.base_url
        response = requests.get(url)
        return response.status_code == 200

    def create_account(self, data):
        url = self.base_url + CREATE_ACCOUNT
        response = requests.post(url, json=data)
        if response.ok:
            self.auth_header = response.headers[AUTH_HEADER]
        return response.json()


class User():
    def __init__(self):
        self.username = 'user_' + random_str(3)
        self.password = random_str(10)
        self.requests = Requests()

    @property
    def email(self):
        return f"{self.username}@cloudclient.com"

    @property
    def data(self):
        return {"email": self.email,
                "password": self.password,
                "username": self.username}

    def describe(self):
        print(f"Username: '{self.username}'")
        print(f"Email: '{self.email}'")
        print(f"Password: '{self.password}'")

    def create_account(self):
        res = self.requests.create_account(self.data)
        print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":

    user = User()
    # user.describe()
    # print(user.data)

    user.create_account()
