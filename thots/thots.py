import asyncio
import time

from logger import get_logger
from Utils.utils import URL_BASE

from thots.thot_parse import alt_thot_parse, parse_album, thot_parse

log = get_logger(__name__)


class Thots:
    def __init__(self, config, id_config):
        self.config = config
        self.id_config = id_config
        self.thots = [
            angelhotoficial,
            bumbumgigante,  # has_topic
            casalblond,
            elaquer,
            emilysales,
            hannafallow,
            ilovemymistress,
            kemilyoliveira,
            tatycasadinha,
            afroditehotwife,  # has_topic
            agathalira,  # has_topic
            barbaracastroo,  # has_topic
            bellacasada,  # has_topic
            casalruivaecornooficial,  # has_topic
            casaltopbessa,  # has_topic
            esposagulosinha,  # has_topic
            fabioeanaes,  # has topic
            helenafilmes,  # has_topic
            lualencar11,  # has_topic
            melissadias,  # has_topic
            nicoleballs_trans,  # has_topic
            nikkecasada,  # has_topic
            vidasafada,  # has_topic
        ]
        self.enable = [x.__name__ for x in self.thots if self.config[f"{x.__name__}"]["enable_task"]]
        
    def run(self):
        for i in range(len(self.enable)):
            log.info(f"Iniciando tarefa {self.enable[i]}, {i + 1} de {len(self.enable)}")
            self.thots[i](self.config, self.id_config, self.enable[i])
            log.warning(f"---------------| {self.enable[i]} - Fim da lista de videos.")

    # def run(self):
    #     for i in range(len(self.thots)):
    #         if self.config[f"{self.thots[i].__name__}"]["enable_task"]:
    #             log.info(f"Iniciando tarefa {self.thots[i].__name__}, {i + 1} de {len(self.thots)}")
    #             self.thots[i](self.config, self.id_config, self.thots[i].__name__)
    #             log.warning(f"---------------| {self.thots[i].__name__} - Fim da lista de videos.")


def afroditehotwife(config, id_config, thot):
    folder_link = f"{URL_BASE}EnpudB-I8hRGlkVjeIky0_cBXNzyDY-Ag_Dvm6Kqw1RQfQ"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def agathalira(config, id_config, thot):
    folder_link = f"{URL_BASE}EgU0RTxc0thCoDWSHkFw8IwBwK-UZ_Okzyv725Qp6YuFLg"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def angelhotoficial(config, id_config, thot):
    folder_link = f"{URL_BASE}Ethi7dzQ3kVApyHGlbJIfcUB97aLqQE3jaf0CtH5MqI0pA"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def bellacasada(config, id_config, thot):
    folder_link = f"{URL_BASE}EjsE5AIRCgZOt2kWENHa7zsB3jylhwix9T_WTIvYMtl5Xg"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def casalblond(config, id_config, thot):
    folder_link = f"{URL_BASE}EsclexMG9qdMuq4wTXGq2YIBfuDWESW_PEMncF0lGbZOEg"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def casalruivaecornooficial(config, id_config, thot):
    folder_link = f"{URL_BASE}EhjQgaMMN5pIjdvY59gWhqkBPJSec0KZZLugbmb3BmcGjw"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def casaltopbessa(config, id_config, thot):
    folder_link = f"{URL_BASE}EogbMUeaEpNKnGzJTLmxtpwBtNbFMbl8Cww7FCSuQ0B0GQ"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def esposagulosinha(config, id_config, thot):
    folder_link = f"{URL_BASE}Es_tAJKWL_RHqxOYRPaqxBIBeeo0oAU2UdbnQZaLNc860g"
    categoria = ""
    get_category = False
    enable_gallery = False
    if enable_gallery:
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(parse_album(thot, config))
        loop.run_until_complete(future)
        # asyncio.run(parse_album(thot, config))
    else:
        thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def fabioeanaes(config, id_config, thot):
    folder_link = f"{URL_BASE}ErTYQ6Nk365NpJV08PagMQUBHC_A2PJMFCMoATNrgAj46A"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def helenafilmes(config, id_config, thot):
    folder_link = f"{URL_BASE}EtCI1OHKu_5JmvM2xXUjAm4Bn7EpdWcfZydSEn96fQpCHA"
    categoria = ""
    get_category = False
    enable_gallery = False
    if enable_gallery:
        asyncio.run(parse_album(thot, config))
    else:
        thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def melissadias(config, id_config, thot):
    folder_link = f"{URL_BASE}ElXzKHYCqZxGvFM-zJvdnUkBDQ8KYDNWWmPUdkc2jYWVtA"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def nikkecasada(config, id_config, thot):
    folder_link = f"{URL_BASE}EilrTuIWGGlBmQBjEBTsP8QB6aJJpMqQukV4JTP0AFSaSg"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def vidasafada(config, id_config, thot):
    folder_link = f"{URL_BASE}EjGEHkeddblJlANFY_Bw5xQBYZtR5x_Da05pCLhXzlQJgg"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def elaquer(config, id_config, thot):
    folder_link = f"{URL_BASE}EjSINnPKG7lIok9X7y8VHs4BnM0cvJ-jhT3gUuvN7AH5zA"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def bumbumgigante(config, id_config, thot):
    folder_link = f"{URL_BASE}EprTVCvUlmJKvJNy3vIosDoBuemR3lsuAlSFdwg1u2_lWg"
    categoria = "acompanhada"
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def emilysales(config, id_config, thot):
    folder_link = f"{URL_BASE}EgBbA6dE7lBDqlzg68tzc-IBkRNfIROauurZtSflO-1m5A"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def kemilyoliveira(config, id_config, thot):
    folder_link = f"{URL_BASE}EskGVwYP_NZFg78mbAGamvsBRTeT5ZOxRz-puVxEWxzG1Q"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def barbaracastroo(config, id_config, thot):
    folder_link = f"{URL_BASE}EqZtHltDAp9NjO25O3wzUl4Bw_6c3WBeL6R6acSM3hq65A"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def nicoleballs_trans(config, id_config, thot):
    folder_link = f"{URL_BASE}EnJdthtnJt9Fv2xWnGeWZ8cB4pb1yqOuC2xfAZI3kY86xQ"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def lualencar11(config, id_config, thot):
    folder_link = f"{URL_BASE}EtwI68PKnSBAq4cyGUIWXbgBQAsoXATcaLBw9eEiwSCTyA"
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def hannafallow(config, id_config, thot):
    folder_link = ""
    categoria = ""
    get_category = False
    thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def tatycasadinha(config, id_config, thot):
    folder_link = ""
    categoria = ""
    get_category = False
    alternative = True
    if alternative:
        asyncio.run(alt_thot_parse(thot, config, id_config))
    else:
        thot_parse(thot, folder_link, config, id_config, categoria, get_category)


def ilovemymistress(config, id_config, thot):
    folder_link = ""
    categoria = ""
    get_category = False
    alternative = True
    if alternative:
        asyncio.run(alt_thot_parse(thot, config, id_config))
    else:
        thot_parse(thot, folder_link, config, id_config, categoria, get_category)
