# bot/main.py

import logging

from bot.app import create_application


def main():
    # ============================================================
    # SAFE LOGGING CONFIG (token-safe)
    # ============================================================
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # Silence noisy libraries
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logging.info("✅ Logging initialized (token-safe)")

    # ============================================================
    # CREATE TELEGRAM APPLICATION (v20+)
    # ============================================================
    application = create_application()

    logging.info("🚀 AnonyLink bot starting (polling mode)...")

    # ============================================================
    # RUN POLLING — SAFE, SINGLE INSTANCE
    # ============================================================
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=None,
        close_loop=False,
    )


if __name__ == "__main__":
    main()
