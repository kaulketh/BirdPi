"""
Telegram inline keyboards for BirdPi.
"""

from enum import StrEnum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Callback(StrEnum):
    CONFIRM_CLEAR_IMAGES = "confirm_clear_images"
    CONFIRM_CLEAR_VIDEOS = "confirm_clear_videos"
    CONFIRM_EVENT_DELETE_IMAGE = "confirm_event_delete_image"
    CONFIRM_EVENT_DELETE_VIDEO = "confirm_event_delete_video"
    CONFIRM_LATEST_IMAGE_DELETE = "confirm_latest_image_delete"
    CONFIRM_SERVICE_STOP = "confirm_service_stop"
    CONFIRM_SERVICE_RESTART = "confirm_service_restart"

    EVENTS = "events"
    LATEST_EVENT = "latest_event"

    LATEST_IMAGE = "latest_image"
    LATEST_IMAGE_CANCEL = "latest_image_cancel"

    MAIN = "main_menu"
    MANUAL_VIDEOS = "manual_videos"
    MANUAL_VIDEO = "manual_video"
    MANUAL_VIDEO_DELETE_REQUEST = "manual_video_delete_request"
    CONFIRM_MANUAL_VIDEO_DELETE = "confirm_manual_video_delete"
    SERVICE = "service"
    STORAGE = "storage"


class ButtonLabel(StrEnum):
    BACK = "⬅ Back"
    CANCEL = "Cancel"


def _auto_emoji(text: str) -> str:
    t = text.lower()

    if "restart" in t:
        return f"🔄 {text}"
    if "delete" in t:
        return f"🗑️ {text}"
    if "stop" in t:
        return f"⛔ {text}"
    if "yes" in t:
        return f"✅ {text}"
    if "cancel" in t:
        return f"❌ {text}"

    return text


def _make_confirm_dialog(
        yes_label: str,
        yes_callback: Callback | str,
        cancel_label: str,
        cancel_callback: Callback | str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    _auto_emoji(yes_label),
                    callback_data=yes_callback,
                )
            ],
            [
                InlineKeyboardButton(
                    _auto_emoji(cancel_label),
                    callback_data=cancel_callback,
                )
            ],
        ]
    )


def confirm_clear_images() -> InlineKeyboardMarkup:
    return _make_confirm_dialog(
        "Yes, delete all images",
        Callback.CONFIRM_CLEAR_IMAGES,
        ButtonLabel.CANCEL,
        Callback.STORAGE,
    )


def confirm_clear_videos() -> InlineKeyboardMarkup:
    return _make_confirm_dialog(
        "Yes, delete all videos",
        Callback.CONFIRM_CLEAR_VIDEOS,
        ButtonLabel.CANCEL,
        Callback.STORAGE,
    )


def confirm_delete_event_image() -> InlineKeyboardMarkup:
    return _make_confirm_dialog(
        "Yes, delete image",
        Callback.CONFIRM_EVENT_DELETE_IMAGE,
        ButtonLabel.CANCEL,
        Callback.LATEST_EVENT,
    )


def confirm_delete_event_video() -> InlineKeyboardMarkup:
    return _make_confirm_dialog(
        "Yes, delete video",
        Callback.CONFIRM_EVENT_DELETE_VIDEO,
        ButtonLabel.CANCEL,
        Callback.LATEST_EVENT,
    )


def confirm_delete_latest_image() -> InlineKeyboardMarkup:
    return _make_confirm_dialog(
        "Yes, delete image",
        Callback.CONFIRM_LATEST_IMAGE_DELETE,
        ButtonLabel.CANCEL,
        Callback.LATEST_IMAGE_CANCEL,
    )


def confirm_service_restart() -> InlineKeyboardMarkup:
    return _make_confirm_dialog(
        "Yes, restart BirdPi",
        Callback.CONFIRM_SERVICE_RESTART,
        ButtonLabel.CANCEL,
        Callback.SERVICE,
    )


def confirm_service_stop() -> InlineKeyboardMarkup:
    return _make_confirm_dialog(
        "Yes, stop BirdPi",
        Callback.CONFIRM_SERVICE_STOP,
        ButtonLabel.CANCEL,
        Callback.SERVICE,
    )


def confirm_delete_manual_video(
        filename: str,
) -> InlineKeyboardMarkup:
    return _make_confirm_dialog(
        "Yes, delete video",
        f"{Callback.CONFIRM_MANUAL_VIDEO_DELETE}:{filename}",
        ButtonLabel.CANCEL,
        f"{Callback.MANUAL_VIDEO}:{filename}",
    )


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(

        [
            [
                InlineKeyboardButton(
                    "🐾 Observation",
                    callback_data="observation",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🕊 Latest Event",
                    callback_data=Callback.LATEST_EVENT,
                ),
                InlineKeyboardButton(
                    "🖼 Latest Image",
                    callback_data=Callback.LATEST_IMAGE,
                ),
            ],
            [
                InlineKeyboardButton(
                    "📚 Events",
                    callback_data=Callback.EVENTS,
                ),
                InlineKeyboardButton(
                    "💾 Storage",
                    callback_data=Callback.STORAGE,
                ),
            ],
            [
                InlineKeyboardButton(
                    "🎬 Manual Videos",
                    callback_data=Callback.MANUAL_VIDEOS,
                ),
            ],
            [
                InlineKeyboardButton(
                    "⚙ Service",
                    callback_data=Callback.SERVICE,
                ),
                InlineKeyboardButton(
                    "🛠 Manual Control",
                    callback_data="manual_control",
                ),
            ],
        ]
    )


def observation_keyboard(
        current_mode: str,
) -> InlineKeyboardMarkup:
    bird_label = (
        "✅ 🐦 Bird"
        if current_mode == "bird"
        else "🐦 Bird"
    )

    wildlife_label = (
        "✅ 🦊 Wildlife"
        if current_mode == "wildlife"
        else "🦊 Wildlife"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    bird_label,
                    callback_data="observation_bird",
                ),
                InlineKeyboardButton(
                    wildlife_label,
                    callback_data="observation_wildlife",
                ),
            ],
            [
                InlineKeyboardButton(
                    ButtonLabel.BACK,
                    callback_data=Callback.MAIN,
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
                    ButtonLabel.BACK,
                    callback_data=Callback.MAIN,
                ),
            ],
        ]
    )


def service_menu(running: bool, ) -> InlineKeyboardMarkup:
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
                ButtonLabel.BACK,
                callback_data=Callback.MAIN,
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def event_menu(has_image: bool, has_video: bool, ) -> InlineKeyboardMarkup:
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
                ButtonLabel.BACK,
                callback_data=Callback.EVENTS,
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def events_menu(events, page: int, has_previous: bool,
                has_next: bool, ) -> InlineKeyboardMarkup:
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
                ButtonLabel.BACK,
                callback_data=Callback.MAIN,
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def manual_videos_menu(
        videos,
        page: int,
        has_previous: bool,
        has_next: bool,
) -> InlineKeyboardMarkup:
    buttons = []

    for video in videos:
        label = video.stem.removeprefix(
            "manual_"
        )

        buttons.append(
            [
                InlineKeyboardButton(
                    f"🎥 {label}",
                    callback_data=f"manual_video:{video.name}",
                )
            ]
        )

    navigation = []

    if has_previous:
        navigation.append(
            InlineKeyboardButton(
                "⬅ Previous",
                callback_data=f"manual_videos_page:{page - 1}",
            )
        )

    if has_next:
        navigation.append(
            InlineKeyboardButton(
                "Next ➡",
                callback_data=f"manual_videos_page:{page + 1}",
            )
        )

    if navigation:
        buttons.append(navigation)

    buttons.append(
        [
            InlineKeyboardButton(
                ButtonLabel.BACK,
                callback_data=Callback.MAIN,
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def manual_video_menu(
        filename: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎥 Send Video",
                    callback_data=f"manual_video_send:{filename}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🗑 Delete Video",
                    callback_data=f"{Callback.MANUAL_VIDEO_DELETE_REQUEST}:{filename}",
                ),
            ],
            [
                InlineKeyboardButton(
                    ButtonLabel.BACK,
                    callback_data=f"{Callback.MANUAL_VIDEO}:{filename}",
                ),
            ],
        ]
    )


def latest_image_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🗑 Delete Image",
                    callback_data="latest_image_delete",
                )
            ],
            [
                InlineKeyboardButton(
                    ButtonLabel.BACK,
                    callback_data="latest_image_back",
                )
            ],
        ]
    )


def manual_control_menu(manual_video_active: bool, ) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                "📸 Capture",
                callback_data="manual_capture",
            ),
        ],
    ]

    if manual_video_active:
        buttons.append(
            [
                InlineKeyboardButton(
                    "⏹ Video Stop",
                    callback_data="manual_video_stop",
                ),
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    "🎥 Video Start",
                    callback_data="manual_video_start",
                ),
            ]
        )

    buttons.extend(
        [
            [
                InlineKeyboardButton(
                    "IR Off",
                    callback_data="manual_ir_off",
                ),
                InlineKeyboardButton(
                    "IR Left",
                    callback_data="manual_ir_left",
                ),
            ],
            [
                InlineKeyboardButton(
                    "IR Right",
                    callback_data="manual_ir_right",
                ),
                InlineKeyboardButton(
                    "IR Both",
                    callback_data="manual_ir_both",
                ),
            ],
            [
                InlineKeyboardButton(
                    ButtonLabel.BACK,
                    callback_data=Callback.MAIN,
                ),
            ],
        ]
    )

    return InlineKeyboardMarkup(buttons)
