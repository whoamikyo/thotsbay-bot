import datetime
import json
import os
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor

import yt_dlp as youtube_dl
from dotenv import load_dotenv
from logger import get_logger

import Utils.thotshub as thotsbay
from Utils.thumb_maker import Thumbmaker
from Utils.utils import (
    ID_CONFIG,
    LATEST_POST_URL,
    REFERER,
    THOTSBAY_PW,
    THOTSBAY_USER,
    DateTimeEncoder,
    absolute_file_paths,
    clean_tmp,
    get_files_in_path_without_extension,
    get_time_diff,
    request_api,
    slugify,
    thumbnails_path,
    truncate_string,
)

load_dotenv()

log = get_logger(__name__)

thotsbay.Account = thotsbay.Account(THOTSBAY_USER, THOTSBAY_PW)

# YT-DLP referer
youtube_dl.utils.std_headers["Referer"] = REFERER

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


def download_upload(path, link, i, j, has_topic, folder_link, payload, thot, enable_posting, remaining, contador, max_posts_at_once):

    name = slugify(str(i) + "-" + j)
    download_file = truncate_string(path + name) + ".mp4"
    log.info(f"Baixando {download_file}")
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
            request_api(ID_CONFIG, payload, mode="PUT")
            log.warning(f"Arquivo não encontrado no servidor, ainda faltam {remaining} arquivos.")
    if not os.path.isfile(download_file):
        log.critical(f"Erro ao baixar o arquivo {i}, com o nome: {name}")
    else:
        log.info(f"Arquivo {name} baixado com sucesso! Agora...Enviando...")
        subprocess.call(cmd, shell=True)
        remaining = remaining - contador
        request_api(ID_CONFIG, payload, mode="PUT")
        log.info(f"Arquivo {name} enviado com sucesso, ainda faltam: {remaining}")

    if has_topic > 0 and enable_posting:
        if max_posts_at_once <= 9 and remaining > 0:
            log.info(f"Ainda faltam {remaining}, a postagem será feita depois para evitar flood...")
        else:
            log.info("Prosseguindo com a postagem...")
            check_latest_post = request_api(LATEST_POST_URL, mode="GET")
            latest_post = datetime.datetime.fromisoformat(check_latest_post[thot])  # type: ignore
            agora = datetime.datetime.utcnow()
            diff_minutes = get_time_diff(start=latest_post, end=agora)
            if diff_minutes > 1:
                log.info(f"A última postagem foi em {latest_post} a diferença é: {int(diff_minutes)} minutos")
                path_list = absolute_file_paths(path)
                imgur_list = [Thumbmaker().get_thumb_upload(path, name=thot) for path in path_list]
                lista_nomes = get_files_in_path_without_extension(path)
                log.info("Atualizando tópico agora...")
                thotsbay.Account.send_message_in_thread(has_topic, msg(imgur_list, folder_link, lista_nomes))
                latest_post_payload = json.dumps({thot: datetime.datetime.utcnow()}, cls=DateTimeEncoder)
                request_api(LATEST_POST_URL, latest_post_payload, mode="PUT")
                # Pruning temporary files
                clean_tmp(path)
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
    tabela = [titulo.format(lista_nomes[i]) + linha.format("".join([coluna.format(a) for a in item])) for i, item in enumerate(lista_urls)]

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
            request_api(ID_CONFIG, payload, mode="PUT")
            log.warning("Arquivo não encontrado no servidor, ainda faltam arquivos.")
    if not os.path.isfile(download_file):
        log.critical(f"Erro ao baixar o arquivo {i}, com o nome: {name}")
    else:
        log.info(f"Arquivo {name} baixado com sucesso! Agora...Enviando...")
        subprocess.call(cmd, shell=True)
        request_api(ID_CONFIG, payload, mode="PUT")
        log.info(f"Arquivo {name} enviado com sucesso")
