import hydra
from threading import Thread
from app.utils.common import init_from_cfg
from app.data_layer.data_saver.data_saver import DataSaver
from pathlib import Path
from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


@hydra.main(config_path="../../configs", config_name="data_saver", version_base=None)
def main(cfg):
    savers = []
    for data_saver in cfg.data_saver:
        data_saver_name, data_saver_cfg = list(data_saver.items())[0]
        saver = init_from_cfg(data_saver_cfg, DataSaver)
        saver_thread = Thread(target=saver.retrieve_and_save)
        logger.info(f"Starting the saver {data_saver_name}")
        saver_thread.start()
        savers.append(saver)
    for saver in savers:
        saver_thread.join()


if __name__ == "__main__":
    main()
