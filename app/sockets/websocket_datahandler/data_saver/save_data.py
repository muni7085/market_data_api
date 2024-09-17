from app.sockets.websocket_datahandler.data_saver import DataSaver
from app.sockets.websocket_datahandler.on_data_callbacks import BaseCallback
import hydra
from omegaconf import OmegaConf
from app.utils.common.instantiation import init_from_cfg

@hydra.main("../../../configs",config_name="data_saver",version_base=None)
def main(cfg):
    print(OmegaConf.to_container(cfg,resolve=True))

    data_saver = init_from_cfg(cfg,DataSaver)
    if data_saver is not None:
        data_saver.retrieve_and_save()

if __name__ == "__main__":
    main()