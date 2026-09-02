"""
Telegram bot entry point for BirdPi.
"""

import os

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
)

from birdpi.bootstrap import initialize
from birdpi.runtime.status import RuntimeStatusStore
from birdpi.storage import Storage
from birdpi.telegram.handlers import (
    error_handler,
    menu_callback,
    start,
    status,
)
from birdpi.web.service import BirdPiService


def main() -> None:
    config = initialize()

    token = os.environ[
        config.telegram.token_env
    ]

    chat_id = int(
        os.environ[
            config.telegram.chat_id_env
        ]
    )

    storage = Storage(config)

    runtime_status = RuntimeStatusStore(
        config.runtime_status_path
    )

    service = BirdPiService()

    application = (
        Application
        .builder()
        .token(token)
        .build()
    )

    application.bot_data["config"] = config
    application.bot_data["storage"] = storage
    application.bot_data["runtime_status"] = runtime_status
    application.bot_data["service"] = service
    application.bot_data["chat_id"] = chat_id

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("status", status)
    )

    application.add_handler(
        CallbackQueryHandler(menu_callback)
    )

    application.add_error_handler(
        error_handler
    )

    application.run_polling()


if __name__ == "__main__":
    main()
