from thots.thots import Thots
from logger import get_logger
from Utils.thotshub import Account
from Utils.utils import CONFIG_BACKUP, ID_CONFIG, backup_id, check_colab, request_api, write_ids, ENABLE_TASK, headers_backup

log = get_logger(__name__)


if __name__ == "__main__":

    Account.check_thotsbay()
    check_colab()
    config = request_api(CONFIG_BACKUP, headers=headers_backup, mode="GET")
    enable_task = request_api(ENABLE_TASK, headers=headers_backup, mode="GET")
    id_config = request_api(ID_CONFIG, mode="GET")

    Thots(config, id_config, enable_task).run()

    log.info("Todas as tarefas foram finalizadas")
    log.info("Salvando ID's da API localmente....")
    backup_id()
    write_ids(request_api(ID_CONFIG, mode="GET"))
