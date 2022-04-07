import traceback

import requests
from bs4 import BeautifulSoup as bs
from logger import get_logger
from .utils import MakeRequest

log = get_logger(__name__)


class Error(Exception):
    """Base class for other exceptions"""

    pass


class ParseTokenError(Error):
    """Token can`t be parsed"""

    pass


class ThreadMessage:
    def __init__(self, userId: int, nickname: str, message: str, fullMessage, messageId):
        self.messageId = messageId
        self.userId = userId
        self.nickname = nickname
        self.message = message
        self.fullMessage = fullMessage


class Account:
    def __init__(self, login: str, password: str):
        try:
            self.login = login
            self.password = password
            self.url_base = "https://forum.thotsbay.com/"
            self.url_login = f"{self.url_base}login/login"
            # self.client = requests.Session()
            self.request = MakeRequest()
            self.update_token()
        except requests.RequestException:
            traceback.print_exc()
            pass

    def update_token(self):
        req = self.request.get(self.url_login).text
        soup = bs(req, "html.parser")
        self.token = soup.find("input", {"name": "_xfToken"})
        if self.token is None:
            raise ParseTokenError
        else:
            self.token = self.token["value"]  # type: ignore
            log.debug(f"Token: {self.token}")

    def authorize(self):
        log.info("Autorizando...")
        data = {
            "login": self.login,
            "password": self.password,
            "remember": 1,
            "_xfRedirect": self.url_base,
            "_xfToken": self.token,
        }
        log.debug(f"Authorize data: {data}")
        try:
            self.update_token()
            req = self.request.post(self.url_login, data=data).text
            if req.find("Incorrect password") == -1:
                return True
            else:
                return False
        except requests.RequestException:
            traceback.print_exc()
            pass

    def get_messages_in_thread(self, thread: int):
        try:
            self.update_token()
            cMessages = []
            req = self.request.get(f"{self.url_base}threads/{thread}/").text
            soup = bs(req, "html.parser")
            messages = soup.find_all("div", {"class": "message-inner"})
            for message in messages:
                nickname = message.find("h4")
                if nickname is not None:
                    messageId = message.find("div", {"class": "message-userContent lbContainer js-lbContainer"},)[
                        "data-lb-id"
                    ].split("-")
                    messageId = int(messageId[len(messageId) - 1])
                    nickname = nickname.text.replace("\n", "").replace("\t", "").replace("\r", "")
                    userId = int(message.find("a", {"class": "username"})["data-user-id"])
                    text = message.find("div", {"class": "bbWrapper"})
                    msg = str(text)
                    if msg.rfind("</blockquote>") != -1:
                        text = msg[msg.rfind("</blockquote>") + len("</blockquote>") : len(msg)]
                    else:
                        text = text.text
                    cMessages.append(ThreadMessage(userId, nickname, text, msg, messageId))
            return cMessages
        except requests.RequestException:
            traceback.print_exc()
            pass

    def send_message_in_thread(self, thread: int, message: str):

        data = {
            "message_html": message,
            "_xfToken": self.token,
            "_xfWithData": 1,
            "_xfResponseType": "json",
        }
        log.debug(f"Send message data: {data}")
        try:
            self.update_token()
            self.request.post(f"{self.url_base}threads/{thread}/add-reply", data=data)
        except requests.RequestException:
            traceback.print_exc()
            pass

    @staticmethod
    def check_thotsbay():
        """
        Check User and PW
        """
        if Account.authorize():
            log.info("Logado no thotsbay com sucesso.")
            return Account
        else:
            log.critical("Erro ao tentar logar no thotsbay.")
