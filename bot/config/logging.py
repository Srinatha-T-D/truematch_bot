# bot/config/logging.py

import logging
import sys


def setup_logging():
    """
    Global logging configuration for AnonyLink
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
    )

    # Reduce noise from telegram internals
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext").setLevel(logging.INFO)

    logging.info("✅ Logging initialized")
