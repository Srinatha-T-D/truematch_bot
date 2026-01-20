# bot/main.py

import logging
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH)

from bot.app import create_application  # noqa: E402


def main():
    # 🔐 SAFE LOGGING CONFIG
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # 🔕 SILENCE LIBRARIES THAT MAY LOG TOKEN
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logging.info("✅ Logging initialized (token-safe)")

    application = create_application()

    logging.info("🚀 AnonyLink bot starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
