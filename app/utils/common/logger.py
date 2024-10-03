"""
This module provides utility functions for logging.

This module contains a function `get_logger` that returns a logger
object configured with a stream handler and a file handler. The logger
can be used to log messages with different log levels.

Example usage:
    logger = get_logger(__name__)
    logger.info("This is an info message")
    logger.warning("This is a warning message")
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger object configured with a stream handler and a file handler.

    Parameters
    ----------
    name: ``str``
        The name of the logger, this is usually the name of the module

    Returns
    -------
    logger: ``Logger``
        The logger object configured with a stream handler and a file handler

    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler("file.log")
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

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
