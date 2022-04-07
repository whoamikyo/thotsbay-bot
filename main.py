from thots.thots import Thots
from logger import get_logger
import time
from Utils.thotshub import Account
from Utils.utils import CONFIG, ID_CONFIG, backup_id, check_colab, write_ids, MakeRequest

log = get_logger(__name__)


if __name__ == "__main__":

    api = MakeRequest()
    log.info("Checando thotsbay forum...")
    Account.check_thotsbay()
    log.info("Checando colab...")
    check_colab()
    log.info("Checando config...")
    config = api.get(CONFIG).json()
    time.sleep(1)
    log.info("Checando ids...")
    id_config = api.get(ID_CONFIG).json()

    Thots(config, id_config).run()

    log.info("Fazendo backup dos IDs na API backup...")
    backup_id()
    log.info("Salvando ID's da API localmente....")
    write_ids(api.get(ID_CONFIG).json(), filename="json_files/ids_api.json")
    write_ids(api.get(CONFIG).json(), filename="json_files/config_api.json")
