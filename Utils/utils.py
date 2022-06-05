# import asyncio
import asyncio
import base64
import datetime
import json
import os
import re
import subprocess
import time
import unicodedata
from json import JSONEncoder

import aiohttp
import httpcore
from dotenv import load_dotenv
from httpx import (
    Client,
    HTTPError,
    HTTPStatusError,
    InvalidURL,
    NetworkError,
    ReadTimeout,
    RequestError,
    StreamError,
    TimeoutException,
    TooManyRedirects,
)

from logger import get_logger

log = get_logger(__name__)
load_dotenv()
THOTSBAY_USER = os.environ["THOTSBAY_USER"]
THOTSBAY_PW = os.environ["THOTSBAY_PW"]
API_KEY = os.environ["API_KEY"]
ID_CONFIG_WRITE = os.environ["ID_CONFIG_WRITE"]
ID_CONFIG_READ = os.environ["ID_CONFIG_READ"]
CONFIG_READ = os.environ["CONFIG_READ"]
CONFIG_WRITE = os.environ["CONFIG_WRITE"]
IMGUR_CLIENT_ID = os.environ["IMGUR_CLIENT_ID"]
IMGUR_BEARER = os.environ["IMGUR_BEARER"]
CDN = os.environ["CDN"]
URL_BASE = os.environ["URL_BASE"]
CYBERDROP_TOKEN = os.environ["CYBERDROP_TOKEN"]
REFERER = os.environ["REFERER"]
GALLERY = os.environ["GALLERY"]
ID_CONFIG_TESTE = os.environ["ID_CONFIG_TESTE"]
DEVELOPMENT = False
if DEVELOPMENT:
    ID_CONFIG_WRITE = ID_CONFIG_TESTE
    log.info("Ambiente de desenvolvimento ativado")
    log.info(f"URL da API: {ID_CONFIG_READ}")
    log.info(f"URL da API CONFIG: {CONFIG_READ}")
else:
    ID_CONFIG_WRITE = ID_CONFIG_WRITE
    log.info("Ambiente de produção ativado")
headers = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY,
    "X-Bin-Meta": "false",
}
headers_scrapy = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4922.0 Safari/537.36 Edg/101.0.1198.0",
    "referer": f"{REFERER}",
}
regexID = r"/video/([\d]+)\""
regexName = r"<span\b[^>]*>(.*?)</span>"
regexID_Album = r"album/([\d]+)\" class"
regexName_Album = r"jpg\" alt=\"([\w\s\-?]+)"
RegexRange = r"([\d]+)'\s*.class=\"page-link\">>></a></li>"
regexCount = r"data-to=\"([\d]+)"
regexGetCategory = r"/videos/([-?A-Z]+)\">"
regexGetRangeSize = r"([\d]+)\.jpg"
download_path = "Downloads/"
tmp = "tmp/"
if not os.path.exists(tmp):
    os.makedirs(tmp)
if not os.path.exists(download_path):
    os.makedirs(download_path)
thumbnails_path = "Thumbnails/"
if not os.path.exists(thumbnails_path):
    os.makedirs(thumbnails_path)


class MakeRequest:
    def __init__(self):
        self.session = Client()
        self.max_retries = 3
        self.sleep_between_retries = 1
        self.tries = 0

    def request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs, follow_redirects=True)
        while self.tries < self.max_retries:
            try:
                response.raise_for_status()
                if response.status_code == 200:
                    log.info(
                        f"Requisição <<{method}>> realizada com sucesso, status code: {response.status_code}"
                    )
                    return response
                else:
                    continue
            except (
                HTTPError,
                NetworkError,
                RequestError,
                InvalidURL,
                StreamError,
                TimeoutException,
                TooManyRedirects,
                HTTPStatusError,
                ReadTimeout,
                TimeoutError,
                httpcore.ReadTimeout,
            ) as e:
                log.error(str(e))
                self.tries += 1
                log.warning(f"Tentando novamente, {self.tries}/{self.max_retries}")
                time.sleep(self.sleep_between_retries)
                if self.tries == self.max_retries:
                    log.critical(f"Critical error: {e}, saindo...")
                    raise SystemExit(e)
                continue
        return response


class DateTimeEncoder(JSONEncoder):
    """
    Custom encoder to handle datetime objects
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(DateTimeEncoder, self).default(obj)


def clean_tmp(path):
    """
    Delete all files in a directory
    """
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as err:
            log.warning(f"Erro ao deletar arquivo: {err}")


def check_colab():
    """
    Check colab enviorement
    """
    if "COLAB_GPU" in os.environ:
        log.info("COLAB enviorement detected")
        return True
    else:
        log.info("COLAB enviorement not detected")
        return False


async def async_request_main(url, data=None, mode=None):
    """
    return html from url

    """
    async with aiohttp.ClientSession() as client:

        # tasks = []
        tasks = [asyncio.ensure_future(make_request(client, url))]
        # tasks.append(asyncio.ensure_future(make_request(client, url)))

        await asyncio.gather(*tasks)
        # return retorno


async def make_request(session, url):
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4922.0 Safari/537.36 Edg/101.0.1198.0"
    # }

    try:
        async with session.get(url) as response:

            response = await response.text()

            if response.status != 200:
                return {"error": f"server returned {response.status}"}
            else:
                return re.findall(regexID, response)
    except asyncio.TimeoutError as e:
        log.error(f" - TimeoutError: {e}")
        return {"results": f"timeout error on {url}"}


def image_uploader(filelist):

    imgur_url = "https://api.imgur.com/3/upload"
    imgur_headers = {"Authorization": f"Bearer {IMGUR_BEARER}"}
    cyberdrop_upload_url = "https://cyberdrop.me/api/upload"
    cyberdrop_header = {
        "token": f"{CYBERDROP_TOKEN}",
        "albumid": "90539",
        "Content-Type": "multipart/form-data",
    }
    total_file_number = len(filelist)
    file_index = 1
    upload = MakeRequest()
    # url_list = [upload.request("POST", imgur_url, headers=imgur_headers, data={"image": convert_to_b64(file), "album": "0S5j3ML"}) for file in filelist]
    url_list = []
    for file in filelist:
        log.info(f"Enviando imagem {file_index} de {total_file_number} : {file}")
        file_index = file_index + 1
        # file_64 = convert_to_b64(file)
        data = {
            "image": convert_to_b64(file),
            "type": "base64",
            "album": "uZGNuSu",
        }
        url = upload.request(
            "POST", imgur_url, headers=imgur_headers, data=data
        ).json()["data"]["link"]
        log.debug(f"URL: {url}")
        success = url
        if success:
            log.info(f"{file} enviado com sucesso")
            url_list.append(url)
        else:
            # fallback to cyberdrop
            # files = {"files[]": convert_to_b64(file)}
            files = {"files[]": open(file, "rb")}
            log.debug(f"Enviando: {files}")
            url = upload.request(
                "POST", cyberdrop_upload_url, headers=cyberdrop_header, files=files
            ).json()["files"][0]["url"]
            log.debug(f"URL: {url}")
            success = url
            if success:
                log.info(f"{file} enviado com sucesso")
                url_list.append(url)
    return url_list


def convert_to_b64(file):
    """
    Convert file to base64
    """
    with open(file, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")


def write_ids(req, filename):
    with open(filename, "w") as f:
        json.dump(req, f, sort_keys=True, indent=4)


def write_tmp(content, filename):
    with open(tmp + filename, "a+", encoding="utf-8") as f:
        f.seek(0)
        file = f.read(100)
        if len(file) > 0:
            f.write("\n")
        f.write(f"{content}")
        f.close()


def get_ids_from_json(file_path):
    """Extrai todos os ids de um arquivo json"""
    with open(file_path, "r") as f:
        data = json.load(f)
        ids = re.findall(r"\d+", str(data))
        return ids


def find_duplicates(lista):
    """Acha valores duplicados em uma lista"""
    return list(set([x for x in lista if lista.count(x) > 1]))


def remove_duplicates(lista):
    seen = set()
    seen_add = seen.add
    return [x for x in lista if not (x in seen or seen_add(x))]


def delete_file(filename):
    """
    Deleta arquivos temporarios
    """
    if os.path.exists(tmp + filename):
        os.remove(tmp + filename)


def get_time_diff(start, end):
    """
    Calculate time difference between two datetime objects
    """
    time_delta = end - start
    total_seconds = time_delta.total_seconds()
    diff_minutes = total_seconds / 60
    return round(diff_minutes)


def read_file(filename):
    with open(tmp + filename, "r") as f:
        lines = f.readlines()
        new_items = [x.strip() for x in lines]
        return new_items


def read_file_to_int(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        # lines = ", ".join(map(str, lines))
        new_items = [x[:-1] for x in lines]
        new_items = [int(i) for i in new_items]
        # new_items = [i.replace("'", "") for i in new_items]
        return new_items


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def truncate_string(value, max_length=238, suffix="..."):
    """
    Truncates a string after a certain number of chars.
        value: string to truncate.
        max_length: maximum length of string.
        suffix: string to append to the end of truncated string.
    """
    string_value = str(value)
    string_truncated = string_value[
        : min(len(string_value), (max_length - len(suffix)))
    ]
    suffix = suffix if len(string_value) > max_length else ""
    return string_truncated + suffix


def get_size_of_nested_list(lista):
    """Get number of elements in a nested list
    ie:
    nestedList = [2 ,3, [44,55,66], 66, [5,6,7, [1,2,3], 6] , 10, [11, [12, [13, 24]]]]
    return the number of elements in the nested list
    Another way:
        list_elem = sum([len(nestedList) for nestedList in tmp_list])
    """
    count = 0
    # Iterate over the list
    for elem in lista:
        # Check if type of element is list
        if type(elem) == list:
            # Again call this function to get the size of this element
            count += get_size_of_nested_list(elem)
        else:
            count += 1
    return count


def divide_list(lst, n):
    """
    Divide a list into n chunks
        n: number of chunks
        lst: list to be divided
    """
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def compare_lists(list1, list2):
    """
    Compare two lists and return the difference
    """
    diff = [i for i in list1 + list2 if i not in list1 or i not in list2]
    return diff


def get_list_from_nested(lista):
    """
    Get a list from a nested list
    """
    return [item for sublist in lista for item in sublist]


def convert_range(value):
    """
    convert a str in list to int
    """
    result = [str(item) for item in value]
    _str = "".join(result)
    _int = int(_str)
    return _int


def list_to_int(value):
    """
    Converte valores em lista para int
    """
    result = [int(i) for i in value]
    return result


def get_video_duration(input):
    """Get the duration of a video using ffprobe."""
    cmd = f'ffprobe -i {input} -show_entries format=duration -v quiet -of csv="p=0"'
    output = subprocess.check_output(
        cmd, shell=True, stderr=subprocess.STDOUT
    )  # Let this run in the shell
    # return round(float(output))  # ugly, but rounds your seconds up or down
    return float(output)


def absolute_file_paths(directory):
    """
    Get absolute file paths from a directory
    """
    path = os.path.abspath(directory)
    return [entry.path for entry in os.scandir(path) if entry.is_file()]


def get_files_in_path_without_extension(path):
    """
    Get files in path without extension
    """
    return [
        f.split(".")[0]
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
    ]
