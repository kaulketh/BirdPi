"""
Telegram inline keyboards for BirdPi.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📊 Status",
                    callback_data="status",
                ),
                InlineKeyboardButton(
                    "🕊 Latest Event",
                    callback_data="latest_event",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🖼 Latest Image",
                    callback_data="latest_image",
                ),
                InlineKeyboardButton(
                    "📚 Events",
                    callback_data="events",
                ),
            ],
            [
                InlineKeyboardButton(
                    "💾 Storage",
                    callback_data="storage",
                ),
                InlineKeyboardButton(
                    "⚙ Service",
                    callback_data="service",
                ),
            ],
        ]
    )


def storage_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🗑 Clear Images",
                    callback_data="storage_clear_images",
                ),
                InlineKeyboardButton(
                    "🗑 Clear Videos",
                    callback_data="storage_clear_videos",
                ),
            ],
            [
                InlineKeyboardButton(
                    "⬅ Back",
                    callback_data="main_menu",
                ),
            ],
        ]
    )


def confirm_clear_images() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Yes, delete all images",
                    callback_data="confirm_clear_images",
                ),
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="storage",
                ),
            ],
        ]
    )


def confirm_clear_videos() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Yes, delete all videos",
                    callback_data="confirm_clear_videos",
                ),
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="storage",
                ),
            ],
        ]
    )


def service_menu(
        running: bool,
) -> InlineKeyboardMarkup:
    buttons = []

    if running:
        buttons.append(
            [
                InlineKeyboardButton(
                    "⏹ Stop",
                    callback_data="service_stop",
                ),
                InlineKeyboardButton(
                    "🔄 Restart",
                    callback_data="service_restart",
                ),
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    "▶ Start",
                    callback_data="service_start",
                ),
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="main_menu",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def confirm_service_stop() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Yes, stop BirdPi",
                    callback_data="confirm_service_stop",
                ),
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="service",
                ),
            ],
        ]
    )


def confirm_service_restart() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Yes, restart BirdPi",
                    callback_data="confirm_service_restart",
                ),
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="service",
                ),
            ],
        ]
    )


def event_menu(
        has_image: bool,
        has_video: bool,
) -> InlineKeyboardMarkup:
    buttons = []

    media_row = []

    if has_image:
        media_row.append(
            InlineKeyboardButton(
                "🖼 Send Image",
                callback_data="event_send_image",
            )
        )

    if has_video:
        media_row.append(
            InlineKeyboardButton(
                "🎥 Send Video",
                callback_data="event_send_video",
            )
        )

    if media_row:
        buttons.append(media_row)

    delete_row = []

    if has_image:
        delete_row.append(
            InlineKeyboardButton(
                "🗑 Delete Image",
                callback_data="event_delete_image",
            )
        )

    if has_video:
        delete_row.append(
            InlineKeyboardButton(
                "🗑 Delete Video",
                callback_data="event_delete_video",
            )
        )

    if delete_row:
        buttons.append(delete_row)

    buttons.append(
        [
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="events",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def events_menu(
        events,
        page: int,
        has_previous: bool,
        has_next: bool,
) -> InlineKeyboardMarkup:
    buttons = []

    for event in events:
        buttons.append(
            [
                InlineKeyboardButton(
                    event.started_at.strftime(
                        "%d.%m.%Y %H:%M:%S"
                    ),
                    callback_data=f"event:{event.id}",
                )
            ]
        )

    navigation = []

    if has_previous:
        navigation.append(
            InlineKeyboardButton(
                "⬅ Previous",
                callback_data=f"events_page:{page - 1}",
            )
        )

    if has_next:
        navigation.append(
            InlineKeyboardButton(
                "Next ➡",
                callback_data=f"events_page:{page + 1}",
            )
        )

    if navigation:
        buttons.append(navigation)

    buttons.append(
        [
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="main_menu",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def confirm_delete_event_image() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Yes, delete image",
                    callback_data="confirm_event_delete_image",
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="latest_event",
                )
            ],
        ]
    )


def confirm_delete_event_video() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Yes, delete video",
                    callback_data="confirm_event_delete_video",
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="latest_event",
                )
            ],
        ]
    )
