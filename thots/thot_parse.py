import asyncio
import json
import os
import re
import sys

import aiohttp
from logger import get_logger
from Utils.download import download_alt, download_upload
from Utils.utils import (
    CDN,
    RegexRange,
    convert_range,
    download_path,
    get_list_from_nested,
    list_to_int,
    regexCount,
    regexGetRangeSize,
    regexID,
    regexID_Album,
    regexName,
    regexName_Album,
    request_html,
    slugify,
    truncate_string,
    REFERER,
    GALLERY
)

log = get_logger(__name__)

if sys.platform.startswith("win") and sys.version_info[0] == 3 and sys.version_info[1] >= 8:
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)


def thot_parse(thot, has_topic, folder_link, config, id_config, enable_posting, categoria, get_category):

    url = config[thot]
    id_list = id_config[f"{thot}ID"]
    # if get_category:
    #     categorias = re.findall(regexGetCategory, request_html(url=url + "videos/", mode="GET"), re.MULTILINE | re.IGNORECASE)
    #     path_list = [download_path + thot + "/" + categorias[i] + "/" for i in range(len(categorias))]
    #     url_list = [f"{url}videos/{categorias[i]}/" for i in range(len(categorias))]
    #     get_range = get_list_from_nested([re.findall(RegexRange, request_html(url=url_list[i], mode="GET")) for i in range(len(url_list))])
    #     print(get_range)

    if categoria:
        path = f"Download/{thot}/{categoria}/"
        get_range = re.findall(RegexRange, request_html(url=f"{url}videos/{categoria}/", mode="GET"))
        total = False
    else:
        path = f"Downloads/{thot}/"
        get_range = re.findall(RegexRange, request_html(url=f"{url}videos/", mode="GET"))
        total = re.findall(regexCount, request_html(url=url, mode="GET"))
    # max_download_at_once = 0
    if get_range:
        pass
    else:
        get_range = ["1"]

    if categoria:
        url_list = [f"{url}videos/{categoria}/{x}" for x in range(1, convert_range(get_range) + 1)]
    else:
        url_list = [f"{url}videos/{x}" for x in range(1, convert_range(get_range) + 1)]

    if total:
        alt = False
        remaining = int(total[0]) - len(id_list)
        log.info(f"Foi encontrado um total de : {remaining} videos restantes.")
    else:
        alt = True
        log.info("Usando método alternativo para encontrar a quantidade de videos.")
        videoID_alt = get_list_from_nested([re.findall(regexID, request_html(url=x, mode="GET")) for x in url_list])
        log.debug(f"{thot} tmp list: {videoID_alt}")
        remaining = len(videoID_alt) - len(id_list)
        log.info(f"Foi encontrado um total de : {remaining} videos restantes.")

    log.debug(f"Url List: {url_list}")
    if alt:
        log.info("A lista de ID's já foi definida")
        videoID = videoID_alt  # type: ignore
    else:
        log.info("A lista de ID's ainda nao foi definida")
        videoID = get_list_from_nested([re.findall(regexID, request_html(url=x, mode="GET")) for x in url_list])

    videoName = get_list_from_nested([re.findall(regexName, request_html(url=x, mode="GET")) for x in url_list])
    videoID = list_to_int(videoID)

    contador = 0
    max_posts_at_once = 0
    while contador < remaining:
        for i, j in zip(videoID, videoName):
            log.debug(f"Contador: {contador}, Remaining: {remaining}")
            log.debug(f"i: {i}, j: {j}")
            if int(i) not in id_list:
                contador += 1
                log.debug(f"{thot} - Baixando video: {j}")
                # max_download_at_once += 1
                if max_posts_at_once == 10:
                    log.info(f"{thot} - 10 videos foram baixados. Resetando contador.")
                    max_posts_at_once = 0
                log.debug(f"Max posts at once: {max_posts_at_once}")
                max_posts_at_once += 1
                payload = json.dumps({f"{thot}ID": [i]})
                log.debug(f"Payload: {payload}")
                log.debug(f"{thot} - max_posts_at_once: {max_posts_at_once}")
                log.info(f"Download: {contador} of {remaining}")
                link = f"https://{CDN}/hls/{i}/playlist.m3u8"
                log.debug(f"Link: {link}")
                # call yt-dlp download
                download_upload(
                    path, link, i, j, has_topic, folder_link, payload, thot, enable_posting, remaining, contador, max_posts_at_once
                )
    log.info(f"{thot} - Fim da lista de videos.")


async def parse_album(thot, config):

    url = config[thot]
    path = download_path + thot + "/" + "Albums/"
    get_range = re.findall(RegexRange, request_html(url=url + "gallery/", mode="GET"))
    url_list = [f"{url}gallery/{x}" for x in range(1, convert_range(get_range) + 1)]
    AlbumID = get_list_from_nested([re.findall(regexID_Album, request_html(url=x, mode="GET")) for x in url_list])
    AlbumName = get_list_from_nested([re.findall(regexName_Album, request_html(url=x, mode="GET")) for x in url_list])
    RangeSize = get_list_from_nested([re.findall(regexGetRangeSize, request_html(url=x, mode="GET")) for x in url_list])
    RangeSize = list_to_int(RangeSize)
    AlbumID = list_to_int(AlbumID)

    log.debug(f"{thot} - AlbumID: {AlbumID}")
    log.debug(f"RangeSize: {RangeSize}")
    log.debug(f"url_list: {url_list}")
    log.debug(f"get_range: {get_range}")

    tasks = []
    async with aiohttp.ClientSession() as session:
        for i, j in zip(AlbumID, AlbumName):
            log.debug(f"{thot} - Adcionando a lista de tarefas: {j} - ID: {i}")
            for foto_id in range(RangeSize[AlbumID.index(i)] - 100000, RangeSize[AlbumID.index(i)] + 100000):
                if foto_id % 100 == 0:
                    log.debug(f"{thot} - Adcionado a lista de tarefas: {foto_id}")
                url_gallery = f"{GALLERY}/{i}/{foto_id}.jpg"
                tasks.append(asyncio.ensure_future(get_foto(session, url_gallery, path, i, j, foto_id, thot)))
            log.debug(f"{thot} - Fim do album: {j} - ID: {i}")
            await asyncio.gather(*tasks)


async def get_foto(session, url_gallery, path, i, j, foto_id, thot, max_retries=30, sleep_between_retries=3):
    headers = {
        "referer": {REFERER},
    }
    name = slugify(f"{i}-{j}")
    image_path = truncate_string(f"{path}{name}") + f"/{foto_id}.jpg"
    if not os.path.exists(f"{path}{name}"):
        os.makedirs(f"{path}{name}")

    resp = None
    try:
        async with session.get(url_gallery, headers=headers) as response:
            resp = await response.read()
            if response.status != 200:
                return {"error": f"server returned {response.status}"}
            if response.status == 200:
                log.info(f"{thot} - Baixando foto: {foto_id}, AlbumName: {j}, AlbumID: {i}")
                with open(image_path, "wb") as f:
                    f.write(resp)
    except asyncio.TimeoutError as e:
        log.error(f"{thot} - TimeoutError: {e}")
        await asyncio.sleep(5)
        return {"results": f"timeout error on {url_gallery}"}

    return resp


async def alt_thot_parse(thot, config, id_config):
    url_base = config[thot]
    id_list = id_config[f"{thot}ID"]
    try:
        RangeInit = id_list[-1] - 1
    except IndexError as e:
        log.error(f"{thot} - {e}")
        RangeInit = 1
    path = f"Downloads/{thot}/"
    async with aiohttp.ClientSession() as session:
        tasks = []
        for number in range(RangeInit, 86800):
            url = f"{url_base}video/{number}"
            if number % 100 == 99:
                log.debug(f"{thot} - Baixando video: {number}")
            tasks.append(asyncio.ensure_future(get_video_alt(session, url, id_list, path, thot, number)))

        await asyncio.gather(*tasks)


async def get_video_alt(session, url, id_list, path, thot, number):
    pattern = r"Página não localizada! =\("
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4922.0 Safari/537.36 Edg/101.0.1198.0",
        "referer": {REFERER},
    }
    regexName = r"#FFFFFF;\">([^<]+)"
    regexID = r"/video/([\d]+)\","

    # resp = None
    try:
        async with session.get(url, headers=headers) as response:

            resp = await response.text()
            if response.status != 200:
                return {"error": f"server returned {response.status}"}
            if re.findall(pattern, resp) == [] and response.status == 200:
                VideoID = re.findall(regexID, resp)
                VideoName = re.findall(regexName, resp)
                for i, j in zip(VideoID, VideoName):
                    log.debug(f"i: {i}, j: {j}")
                    if int(i) not in id_list:
                        log.debug(f"{thot} - Baixando video: {j}")
                        payload = json.dumps({f"{thot}ID": [int(i)]})
                        log.debug(f"Payload: {payload}")
                        link = f"https://{CDN}/hls/{i}/playlist.m3u8"
                        log.debug(f"Link: {link}")
                        # call yt-dlp download
                        download_alt(path, link, i, j, payload, thot)
    except asyncio.TimeoutError as e:
        log.error(f"{thot} - TimeoutError: {e}")
        return {"results": f"timeout error on {url}"}

    # return resp


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


def get_range_from_list(range_list):
    return [min(range_list) - 999999, max(range_list) + 999999]
