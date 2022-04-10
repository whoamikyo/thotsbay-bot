import asyncio

from logger import get_logger

from thots.thot_parse import alt_thot_parse, parse_album, thot_parse

log = get_logger(__name__)


class Thots:
    def __init__(self, config, id_config):
        self.config = config
        self.id_config = id_config
        self.thots = [
            afroditehotwife,  # has_topic
            agathalira,  # has_topic
            angelhotoficial,
            barbaracastroo,  # has_topic
            bellacasada,  # has_topic
            bumbumgigante,  # has_topic
            casalblond,
            casalruivaecornooficial,  # has_topic
            casaltopbessa,  # has_topic
            elaquer,
            emilysales,
            esposagulosinha,  # has_topic
            fabioeanaes,  # has topic
            hannafallow,
            helenafilmes,  # has_topic
            ilovemymistress,
            kemilyoliveira,
            lualencar11,  # has_topic
            melissadias,  # has_topic
            nicoleballs_trans,  # has_topic
            nikkecasada,  # has_topic
            tatycasadinha,
            vidasafada,  # has_topic
        ]
        self.enable = [x.__name__ for x in self.thots if self.config[f"{x.__name__}"]["enable_task"]]

    def run(self):
        for i in range(len(self.enable)):
            log.warning(f"---------------| Iniciando tarefa {self.enable[i]}, {i + 1} de {len(self.enable)}")
            self.thots[i](self.config, self.id_config, self.enable[i])
            log.warning(f"---------------| {self.enable[i]} - Fim da lista de videos.")


def afroditehotwife(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def agathalira(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def angelhotoficial(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def bellacasada(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def casalblond(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def casalruivaecornooficial(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def casaltopbessa(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def esposagulosinha(config, id_config, thot):
    get_category = False
    enable_gallery = False
    if enable_gallery:
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(parse_album(thot, config))
        loop.run_until_complete(future)
        # asyncio.run(parse_album(thot, config))
    else:
        thot_parse(thot, config, id_config, get_category)


def fabioeanaes(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def helenafilmes(config, id_config, thot):
    get_category = False
    enable_gallery = False
    if enable_gallery:
        asyncio.run(parse_album(thot, config))
    else:
        thot_parse(thot, config, id_config, get_category)


def melissadias(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def nikkecasada(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def vidasafada(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def elaquer(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def bumbumgigante(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def emilysales(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def kemilyoliveira(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def barbaracastroo(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def nicoleballs_trans(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def lualencar11(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def hannafallow(config, id_config, thot):
    get_category = False
    thot_parse(thot, config, id_config, get_category)


def tatycasadinha(config, id_config, thot):
    get_category = False
    alternative = True
    if alternative:
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(alt_thot_parse(thot, config, id_config))
        loop.run_until_complete(future)
        # asyncio.run(alt_thot_parse(thot, config, id_config))
    else:
        thot_parse(thot, config, id_config, get_category)


def ilovemymistress(config, id_config, thot):
    get_category = False
    alternative = True
    if alternative:
        asyncio.run(alt_thot_parse(thot, config, id_config))
    else:
        thot_parse(thot, config, id_config, get_category)
