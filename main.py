import time

from logger import get_logger
from thots.thots import Thots
from Utils.thotshub import Account
from Utils.utils import (
    CONFIG_READ,
    CONFIG_WRITE,
    ID_CONFIG_READ,
    ID_CONFIG_WRITE,
    MakeRequest,
    check_colab,
    headers,
    write_ids,
)

log = get_logger(__name__)


if __name__ == "__main__":

    api = MakeRequest()
    log.info("Checando thotsbay forum...")
    Account.check_thotsbay()
    log.info("Checando colab...")
    check_colab()
    log.info("Checando config...")
    config = api.get(CONFIG_READ, headers=headers).json()
    time.sleep(1)
    log.info("Checando ids...")
    id_config = api.get(ID_CONFIG_READ, headers=headers).json()

    Thots(config, id_config).run()

    log.info("Fazendo backup dos IDs na API backup...")
    # api.put(ID_CONFIG_READ, json=api.get(ID_CONFIG_WRITE).json(), headers=headers_backup)
    # api.put(CONFIG_READ, json=api.get(CONFIG_WRITE).json(), headers=headers_backup)
    log.info("Salvando ID's da API localmente....")
    write_ids(
        api.get(ID_CONFIG_READ, headers=headers).json(),
        filename="json_files/ids_api.json",
    )
    write_ids(
        api.get(CONFIG_READ, headers=headers).json(),
        filename="json_files/config_api.json",
    )
