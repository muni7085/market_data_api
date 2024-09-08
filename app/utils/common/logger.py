import logging


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler("file.log")
    c_handler.setLevel(level)
    f_handler.setLevel(level)

    c_format = logging.Formatter(
        "%(asctime)s - %(name)s:%(lineno)d  - %(levelname)s - %(message)s"
    )
    f_format = logging.Formatter(
        "%(asctime)s - %(name)s:%(lineno)d  - %(levelname)s - %(message)s"
    )
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
