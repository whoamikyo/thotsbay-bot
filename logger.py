import logging
import logging.handlers
import os
import sys
from datetime import date
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import colorlog
from cloudwatch import cloudwatch
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]


class Error(Exception):
    """Base class for other exceptions"""

    pass


class ParseTokenError(Error):
    """Token can`t be parsed"""

    pass


def get_project_root() -> Path:
    return Path(__file__).parent


def fileNameLocation():
    today = date.today()
    return f"{get_project_root()}/Logs/{today.day}-{today.month}-{today.year}.log"


log_colors_config = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red",
}

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fmt = logging.Formatter("%(log_color)s%(levelname)s:%(name)s:%(message)s")
LOG_FILE = fileNameLocation()


def color_handler():
    color_handler = colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s",
        log_colors=log_colors_config,
    )
    return color_handler


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(color_handler())
    return console_handler


def cloudwatch_handler():
    handler = cloudwatch.CloudwatchHandler(
        f"{AWS_ACCESS_KEY_ID}",
        f"{AWS_SECRET_ACCESS_KEY}",
        "us-east-1",
        "Personal",
        "forum.thotsbay.com",
    )

    handler.setFormatter(fmt=logging.Formatter("%(levelname)s - %(module)s - %(message)s"))
    return handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, encoding="UTF-8", when="midnight")
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    # logger.setLevel(logging.WARNING)
    # logger.setLevel(logging.INFO)
    # logger.setLevel(logging.CRITICAL)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # logger.addHandler(cloudwatch_handler())  # type: ignore

    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger

