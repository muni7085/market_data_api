import hydra

from app.sockets.websocket_datahandler.data_saver import DataSaver


@hydra.main(config_path="../../configs", config_name="data_saver", version_base=None)
def main(cfg):
    data_saver: DataSaver = DataSaver.by_name(cfg.data_saver.name).from_cfg(
        cfg.streaming_service
    )

    if data_saver:
        data_saver.retrieve_and_save()


if __name__ == "__main__":
    main()
