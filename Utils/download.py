import datetime
import json
import os
import re
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor

import yt_dlp as youtube_dl
from dotenv import load_dotenv

import Utils.thotshub as thotsbay
from logger import get_logger
from Utils.thumb_maker import Thumbmaker
from Utils.utils import (
    CONFIG_WRITE,
    ID_CONFIG_READ,
    ID_CONFIG_WRITE,
    REFERER,
    THOTSBAY_PW,
    THOTSBAY_USER,
    URL_BASE,
    DateTimeEncoder,
    MakeRequest,
    absolute_file_paths,
    clean_tmp,
    get_files_in_path_without_extension,
    get_time_diff,
    headers,
    headers_scrapy,
    slugify,
    thumbnails_path,
    truncate_string,
)

load_dotenv()

log = get_logger(__name__)

thotsbay.Account = thotsbay.Account(THOTSBAY_USER, THOTSBAY_PW)
api = MakeRequest()

# YT-DLP referer
youtube_dl.utils.std_headers["Referer"] = REFERER
youtube_dl.utils.std_headers[
    "User-Agent"
] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4922.0 Safari/537.36 Edg/101.0.1198.0"

PPE = ProcessPoolExecutor()

# global variables
src = "./Downloads/"
dst = "/Thot/"

# build the shell command
cmd = f"""rclone --verbose \
        --retries 3 \
        --checkers 4 \
        --transfers 8 \
        --stats 10s \
        --exclude="**.part" --exclude="**.ytdl" \
        copy --ignore-existing {src} OneDrive_Edu:{dst}"""


def download_upload(
    path, link, i, j, payload, thot, remaining, contador, max_posts_at_once, config
):

    tries = 0
    max_tries = 5
    has_topic = config[thot]["has_topic"]
    enable_posting = config[thot]["enable_posting"]
    folder_link = f"{URL_BASE}{config[thot]['folder_link']}"
    name = slugify(str(i) + "-" + j)
    download_file = truncate_string(path + name) + ".mp4"
    log.info(f"Baixando {download_file}")
    ydl_opts = {
        "outtmpl": download_file,
        "ignoreerrors": False,
        "verbose": False,
        "nocheckcertificate": True,
    }
    while tries < max_tries:
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(link)
            break
        except Exception as err:
            e = getattr(err, "message", repr(err))
            reg = r"^.*(404)"
            not_found_error = re.findall(reg, e)
            if not_found_error:
                log.error(f"Erro: {not_found_error}")
                # remaining = remaining - contador
                api.request("PUT", ID_CONFIG_WRITE, headers=headers, data=payload)
                api.request("PUT", 
                    ID_CONFIG_READ,
                    json=api.request("GET", ID_CONFIG_WRITE).json(),
                    headers=headers,
                )
                log.warning(
                    f"Arquivo não encontrado no servidor, ainda faltam {remaining} arquivos."
                )
            else:
                tries += 1
                log.error(err)
                log.warning(f"Tentando novamente, {tries}/{max_tries}")
                time.sleep(5)
                if tries == max_tries:
                    log.error(f"Tentativas excedidas para baixar {download_file}")
                    log.warning(
                        f"Pulando esse arquivo, ainda faltam {remaining} arquivos."
                    )
                continue

    if not os.path.isfile(download_file):
        log.critical(f"Erro ao baixar o arquivo {i}, com o nome: {name}")
        failed = True
    else:
        failed = False
        log.info(f"Arquivo {name} baixado com sucesso! Agora...Enviando...")
        subprocess.call(cmd, shell=True)
        remaining = remaining - contador
        log.info(f"Arquivo {name} enviado com sucesso, ainda faltam: {remaining}")
        api.request("PUT", ID_CONFIG_WRITE, headers=headers, data=payload)
        api.request("PUT", ID_CONFIG_READ, json=api.request("GET", ID_CONFIG_WRITE).json(), headers=headers)

    if has_topic > 0 and enable_posting and not failed:
        if max_posts_at_once <= 9 and remaining > 0:
            log.info(
                f"Ainda faltam {remaining}, a postagem será feita depois para evitar flood..."
            )
        else:
            log.info("Prosseguindo com a postagem...")
            latest_post = datetime.datetime.fromisoformat(config[thot]["latest_post"])
            agora = datetime.datetime.utcnow()
            diff_minutes = get_time_diff(start=latest_post, end=agora)
            if diff_minutes > 1:
                log.info(
                    f"A última postagem foi em {latest_post} a diferença é: {int(diff_minutes)} minutos"
                )
                path_list = absolute_file_paths(path)
                imgur_list = [
                    Thumbmaker().get_thumb_upload(path, name=thot) for path in path_list
                ]
                lista_nomes = get_files_in_path_without_extension(path)
                thotsbay.Account.check_thotsbay()
                log.info("Atualizando tópico agora...")
                thotsbay.Account.send_message_in_thread(
                    has_topic, msg(imgur_list, folder_link, lista_nomes)
                )
                latest_post_payload = json.dumps(
                    {thot: {"latest_post": datetime.datetime.utcnow()}},
                    cls=DateTimeEncoder,
                )
                api.request("PUT", CONFIG_WRITE, headers=headers, data=latest_post_payload)
                # Pruning temporary files
                # clean_tmp(path)
                clean_tmp(thumbnails_path)
            else:
                log.info("A útlima postagem foi a menos de 1 hora, no FLOOD please!!!!")


def msg(lista_urls: list, folder_link: str, lista_nomes: list):

    msg = """
    [HEADING=1][COLOR=#5e9ca0][IMG]https://forum.thotsbay.com/emotes/HACKERMANS.gif[/IMG][/COLOR][/HEADING]
    [HEADING=1][COLOR=#5e9ca0]A pasta foi atualizada![/COLOR][/HEADING]
    [HEADING=1][COLOR=#2e6c80][COLOR=#ff6600]Thumbnails:[/COLOR][/COLOR][/HEADING]
    {0}
    [HEADING=1][CENTER][COLOR=#2e6c80][COLOR=#ff6600]Link para a pasta: [URL='{folder_link}'][COLOR=#ff6600]Clicka aqui[/COLOR][/URL][/COLOR][/COLOR][/CENTER][/HEADING]
    [HEADING=2][CENTER][COLOR=#2e6c80][COLOR=#ff6600]Senha abaixo: [QUOTE][CODE]https://forum.thotsbay.com[/CODE][/COLOR][/CENTER][/QUOTE][/HEADING]
    [HEADING=2][CENTER][URL='https://github.com/whoamikyo/thotsbay-bot']Powered by: thotsbay-bot[/URL][/CENTER][COLOR=#2e6c80][/COLOR][/HEADING]
    [TABLE]
    [TR]
    [TD][B][COLOR=#ff6600]Não esqueça do like.
    [LEFT][IMG]https://forum.thotsbay.com/emotes/PepePolice.png[/IMG][/LEFT][/COLOR][/B][/TD]
    [/TR]
    [/TABLE]
    """

    titulo = "[TABLE][TR][TD][HEADING=3][CENTER][COLOR=#5e9ca0]{0}[/COLOR][/CENTER][/HEADING][/TD][/TR][/TABLE]"
    linha = "[TABLE][TR]{0}[/TR][/TABLE]"
    coluna = "[TD][IMG]{0}[/IMG][/TD]"
    tabela = [
        titulo.format(lista_nomes[i])
        + linha.format("".join([coluna.format(a) for a in item]))
        for i, item in enumerate(lista_urls)
    ]

    msg = msg.format("".join(tabela), folder_link=folder_link)
    return msg


def download_alt(path, link, i, j, payload, thot):

    name = slugify(str(i) + "-" + j)
    download_file = truncate_string(path + name) + ".mp4"
    log.info(f"Downloading {download_file}")
    try:
        ydl_opts = {
            "outtmpl": download_file,
            "ignoreerrors": False,
            "verbose": False,
            "nocheckcertificate": True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(link)
    except Exception as err:
        e = getattr(err, "message", repr(err))
        reg = r"^.*(404)"
        not_found_error = re.findall(reg, e)
        if not_found_error:
            log.warning(f"Erro: {not_found_error}")
            # remaining = remaining - contador
            api.request("PUT", ID_CONFIG_WRITE, headers=headers, data=payload)
            log.warning("Arquivo não encontrado no servidor, ainda faltam arquivos.")
    if not os.path.isfile(download_file):
        log.critical(f"Erro ao baixar o arquivo {i}, com o nome: {name}")
    else:
        log.info(f"Arquivo {name} baixado com sucesso! Agora...Enviando...")
        subprocess.call(cmd, shell=True)
        api.request("PUT", ID_CONFIG_WRITE, headers=headers, data=payload)
        log.info(f"Arquivo {name} enviado com sucesso")
