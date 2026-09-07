"""
Telegram handlers for BirdPi.
"""

import asyncio

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from birdpi.exceptions import (
    RuntimeCommandError,
    ServiceControlError,
)
from birdpi.telegram.keyboard import (
    confirm_clear_images,
    confirm_clear_videos,
    confirm_delete_event_image,
    confirm_delete_event_video,
    confirm_delete_latest_image,
    confirm_service_restart,
    confirm_service_stop,
    event_menu,
    events_menu,
    latest_image_menu,
    main_menu,
    manual_control_menu,
    service_menu,
    storage_menu,
)
from birdpi.telegram.messages import (
    build_event_text,
    build_manual_control_text,
    build_service_text,
    build_status_text,
    build_storage_text,
)
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)

EVENTS_PAGE_SIZE = 5

_MAIN_ACTIONS = {
    "main_menu",
    "status",
}

_IMAGE_ACTIONS = {
    "latest_image",
    "latest_image_delete",
    "confirm_latest_image_delete",
    "latest_image_cancel",
    "latest_image_back",
}

_EVENT_ACTIONS = {
    "latest_event",
    "events",
    "event_send_image",
    "event_send_video",
    "event_delete_image",
    "event_delete_video",
    "confirm_event_delete_image",
    "confirm_event_delete_video",
}

_SERVICE_ACTIONS = {
    "service",
    "service_start",
    "service_stop",
    "service_restart",
    "confirm_service_stop",
    "confirm_service_restart",
}

_STORAGE_ACTIONS = {
    "storage",
    "storage_clear_images",
    "storage_clear_videos",
    "confirm_clear_images",
    "confirm_clear_videos",
}

_MANUAL_ACTIONS = {
    "manual_control",
    "manual_capture",
    "manual_video_start",
    "manual_video_stop",
    "manual_ir_off",
    "manual_ir_left",
    "manual_ir_right",
    "manual_ir_both",
}


def authorized(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    allowed_chat_id = context.application.bot_data["chat_id"]

    return (
            update.effective_chat is not None
            and update.effective_chat.id == allowed_chat_id
    )


async def start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not authorized(update, context):
        return

    await update.message.reply_text(
        "🐦 BirdPi",
        reply_markup=main_menu(),
    )


async def status(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not authorized(update, context):
        return

    try:
        text = build_status_text(
            context
        )

    except ServiceControlError as error:
        logger.warning(
            "Telegram status query failed: %s",
            error,
        )

        await update.message.reply_text(
            "⚠ BirdPi service status is currently unavailable."
        )
        return

    await update.message.reply_text(
        text
    )


async def error_handler(
        update: object,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.error(
        "Telegram bot error",
        exc_info=(
            type(context.error),
            context.error,
            context.error.__traceback__,
        ) if context.error else None,
    )


async def show_events_page(
        query,
        context: ContextTypes.DEFAULT_TYPE,
        page: int,
) -> None:
    storage = context.application.bot_data["storage"]

    all_events = storage.events()

    offset = page * EVENTS_PAGE_SIZE
    end = offset + EVENTS_PAGE_SIZE

    events = all_events[offset:end]

    if not events and page > 0:
        page -= 1

        offset = page * EVENTS_PAGE_SIZE
        end = offset + EVENTS_PAGE_SIZE

        events = all_events[offset:end]

    await query.edit_message_text(
        f"📚 Events — Page {page + 1}",
        reply_markup=events_menu(
            events=events,
            page=page,
            has_previous=page > 0,
            has_next=end < len(all_events),
        ),
    )


async def _handle_main_action(
        data: str,
        query,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    match data:
        case "main_menu":
            await query.edit_message_text(
                "🐦 BirdPi",
                reply_markup=main_menu(),
            )

        case "status":
            await query.message.reply_text(
                build_status_text(context)
            )


async def _handle_image_action(
        data: str,
        query,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    storage = context.application.bot_data["storage"]

    match data:
        case "latest_image":
            latest_image = storage.latest_image()

            if latest_image is None:
                await query.answer(
                    "No image available.",
                    show_alert=True,
                )
                return

            context.application.bot_data[
                "selected_image_filename"
            ] = latest_image.name

            with latest_image.open("rb") as file:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=file,
                    caption=f"🖼 {latest_image.name}",
                    reply_markup=latest_image_menu(),
                )

            logger.info(
                "Telegram sent latest image: %s",
                latest_image.name,
            )

        case "latest_image_delete":
            await query.edit_message_caption(
                "⚠ Delete latest image?",
                reply_markup=confirm_delete_latest_image(),
            )

        case "confirm_latest_image_delete":
            filename = context.application.bot_data.get(
                "selected_image_filename"
            )

            if filename is None:
                return

            deleted = storage.delete_image(filename)

            if deleted:
                logger.info(
                    "Telegram deleted image: %s",
                    filename,
                )
            else:
                logger.warning(
                    "Telegram could not delete missing image: %s",
                    filename,
                )

            await query.edit_message_caption(
                "🗑 Image deleted."
                if deleted
                else "Image not found.",
                reply_markup=main_menu(),
            )

        case "latest_image_cancel":
            filename = context.application.bot_data.get(
                "selected_image_filename"
            )

            await query.edit_message_caption(
                caption=f"🖼 {filename}",
                reply_markup=latest_image_menu(),
            )

        case "latest_image_back":
            await query.message.delete()

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🐦 BirdPi",
                reply_markup=main_menu(),
            )


async def _handle_event_action(
        data: str,
        query,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    storage = context.application.bot_data["storage"]

    if data.startswith("events_page:"):
        page = int(
            data.removeprefix("events_page:")
        )

        await show_events_page(
            query,
            context,
            page=page,
        )
        return

    if data.startswith("event:"):
        event_id = data.removeprefix("event:")
        event = storage.event(event_id)

        if event is None:
            await query.answer(
                "Event not found.",
                show_alert=True,
            )
            return

        context.application.bot_data[
            "selected_event_id"
        ] = event.id

        await query.edit_message_text(
            build_event_text(event),
            reply_markup=event_menu(
                has_image=bool(event.images),
                has_video=bool(event.video_filename),
            ),
        )
        return

    match data:
        case "latest_event":
            events = storage.events()

            if not events:
                await query.edit_message_text(
                    "🕊 No events available.",
                    reply_markup=main_menu(),
                )
                return

            event = events[0]

            context.application.bot_data[
                "selected_event_id"
            ] = event.id

            await query.edit_message_text(
                build_event_text(event),
                reply_markup=event_menu(
                    has_image=bool(event.images),
                    has_video=bool(event.video_filename),
                ),
            )

        case "events":
            await show_events_page(
                query,
                context,
                page=0,
            )

        case "event_send_image":
            event_id = context.application.bot_data.get(
                "selected_event_id"
            )

            if event_id is None:
                return

            event = storage.event(event_id)

            if event is None or not event.images:
                await query.answer(
                    "No image available.",
                    show_alert=True,
                )
                return

            image = event.images[0]

            with image.path.open("rb") as file:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=file,
                    caption=f"🖼 {event.id}",
                )

            logger.info(
                "Telegram sent event image: event=%s file=%s",
                event.id,
                image.filename,
            )

        case "event_send_video":
            event_id = context.application.bot_data.get(
                "selected_event_id"
            )

            if event_id is None:
                return

            event = storage.event(event_id)

            if event is None or not event.video_filename:
                await query.answer(
                    "No video available.",
                    show_alert=True,
                )
                return

            video_path = (
                    storage.config.video_path
                    / event.video_filename
            )

            if not video_path.is_file():
                await query.answer(
                    "Video file not found.",
                    show_alert=True,
                )
                return

            with video_path.open("rb") as file:
                await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=file,
                    caption=f"🎥 {event.id}",
                    write_timeout=120,
                    connect_timeout=120,
                    read_timeout=120,
                )

            logger.info(
                "Telegram sent event video: event=%s file=%s",
                event.id,
                event.video_filename,
            )

        case "event_delete_image":
            await query.edit_message_text(
                "⚠ Delete image from this event?",
                reply_markup=confirm_delete_event_image(),
            )

        case "event_delete_video":
            await query.edit_message_text(
                "⚠ Delete video from this event?",
                reply_markup=confirm_delete_event_video(),
            )

        case "confirm_event_delete_image":
            event_id = context.application.bot_data.get(
                "selected_event_id"
            )

            if event_id is None:
                return

            event = storage.event(event_id)

            if event is None or not event.images:
                await query.answer(
                    "No image available.",
                    show_alert=True,
                )
                return

            filename = event.images[0].filename

            storage.delete_image(filename)

            logger.info(
                "Telegram deleted event image: event=%s file=%s",
                event_id,
                filename,
            )

            event = storage.event(event_id)

            if event is None:
                await query.edit_message_text(
                    "Event deleted because no media remains.",
                    reply_markup=main_menu(),
                )
                return

            await query.edit_message_text(
                build_event_text(event),
                reply_markup=event_menu(
                    has_image=bool(event.images),
                    has_video=bool(event.video_filename),
                ),
            )

        case "confirm_event_delete_video":
            event_id = context.application.bot_data.get(
                "selected_event_id"
            )

            if event_id is None:
                return

            event = storage.event(event_id)

            if event is None or not event.video_filename:
                await query.answer(
                    "No video available.",
                    show_alert=True,
                )
                return

            filename = event.video_filename

            storage.delete_video(filename)

            logger.info(
                "Telegram deleted event video: event=%s file=%s",
                event_id,
                filename,
            )

            event = storage.event(event_id)

            if event is None:
                await query.edit_message_text(
                    "Event deleted because no media remains.",
                    reply_markup=main_menu(),
                )
                return

            await query.edit_message_text(
                build_event_text(event),
                reply_markup=event_menu(
                    has_image=bool(event.images),
                    has_video=bool(event.video_filename),
                ),
            )


async def _handle_service_action(
        data: str,
        query,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    service = context.application.bot_data["service"]

    match data:
        case "service":
            await query.edit_message_text(
                build_service_text(context),
                reply_markup=service_menu(
                    service.running()
                ),
            )

        case "service_start":
            service.start()

            logger.info(
                "Telegram started BirdPi service"
            )

            await query.edit_message_text(
                build_service_text(context),
                reply_markup=service_menu(
                    service.running()
                ),
            )

        case "service_stop":
            await query.edit_message_text(
                "⚠ Stop BirdPi service?",
                reply_markup=confirm_service_stop(),
            )

        case "service_restart":
            await query.edit_message_text(
                "⚠ Restart BirdPi service?",
                reply_markup=confirm_service_restart(),
            )

        case "confirm_service_stop":
            service.stop()

            logger.info(
                "Telegram stopped BirdPi service"
            )

            await query.edit_message_text(
                build_service_text(context),
                reply_markup=service_menu(
                    service.running()
                ),
            )

        case "confirm_service_restart":
            service.restart()

            logger.info(
                "Telegram restarted BirdPi service"
            )

            await query.edit_message_text(
                "⚙ BirdPi Service\n\n"
                "Restart completed.",
                reply_markup=service_menu(
                    service.running()
                ),
            )


async def _handle_storage_action(
        data: str,
        query,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    storage = context.application.bot_data["storage"]

    match data:
        case "storage":
            await query.message.reply_text(
                build_storage_text(context),
                reply_markup=storage_menu(),
            )

        case "storage_clear_images":
            await query.edit_message_text(
                "⚠ Delete ALL stored images?\n\n"
                "This cannot be undone.",
                reply_markup=confirm_clear_images(),
            )

        case "storage_clear_videos":
            await query.edit_message_text(
                "⚠ Delete ALL stored videos?\n\n"
                "This cannot be undone.",
                reply_markup=confirm_clear_videos(),
            )

        case "confirm_clear_images":
            deleted = storage.clear_images()

            logger.info(
                "Telegram cleared images: %d deleted",
                deleted,
            )

            await query.edit_message_text(
                f"🗑 Deleted {deleted} image(s).",
                reply_markup=storage_menu(),
            )

        case "confirm_clear_videos":
            deleted = storage.clear_videos()

            logger.info(
                "Telegram cleared videos: %d deleted",
                deleted,
            )

            await query.edit_message_text(
                f"🗑 Deleted {deleted} video(s).",
                reply_markup=storage_menu(),
            )


async def _show_manual_control(
        query,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    status = context.application.bot_data[
        "runtime_status"
    ].read()

    await query.edit_message_text(
        build_manual_control_text(context),
        reply_markup=manual_control_menu(
            status.manual_video_active
        ),
    )


async def _handle_manual_action(
        data: str,
        query,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    service = context.application.bot_data["service"]

    if not service.running():
        await query.edit_message_text(
            "🛠 BirdPi Manual Control\n\n"
            "⚠ BirdPi service is stopped.\n"
            "Manual controls are currently unavailable.",
            reply_markup=main_menu(),
        )
        return

    runtime = context.application.bot_data["runtime"]

    match data:
        case "manual_control":
            await _show_manual_control(
                query,
                context,
            )

        case "manual_capture":
            response = await asyncio.to_thread(
                runtime.capture_image
            )

            logger.info(
                "Telegram requested manual image capture: %s",
                response,
            )

            await query.answer(
                response,
                show_alert=True,
            )

        case "manual_video_start":
            response = await asyncio.to_thread(
                runtime.video_start
            )

            logger.info(
                "Telegram requested manual video start: %s",
                response,
            )

            await query.edit_message_text(
                (
                    "🛠 BirdPi Manual Control\n\n"
                    f"{response}\n"
                    "Video: RECORDING"
                ),
                reply_markup=manual_control_menu(
                    manual_video_active=True
                ),
            )

        case "manual_video_stop":
            response = await asyncio.to_thread(
                runtime.video_stop
            )

            logger.info(
                "Telegram requested manual video stop: %s",
                response,
            )

            await query.edit_message_text(
                (
                    "🛠 BirdPi Manual Control\n\n"
                    f"{response}\n"
                    "Video: IDLE"
                ),
                reply_markup=manual_control_menu(
                    manual_video_active=False
                ),
            )

        case "manual_ir_off":
            await asyncio.to_thread(
                runtime.ir_off
            )

            logger.info(
                "Telegram set IR mode: OFF"
            )

            await _show_manual_control(
                query,
                context,
            )

        case "manual_ir_left":
            await asyncio.to_thread(
                runtime.ir_left
            )

            logger.info(
                "Telegram set IR mode: LEFT"
            )

            await _show_manual_control(
                query,
                context,
            )

        case "manual_ir_right":
            await asyncio.to_thread(
                runtime.ir_right
            )

            logger.info(
                "Telegram set IR mode: RIGHT"
            )

            await _show_manual_control(
                query,
                context,
            )

        case "manual_ir_both":
            await asyncio.to_thread(
                runtime.ir_both
            )

            logger.info(
                "Telegram set IR mode: BOTH"
            )

            await _show_manual_control(
                query,
                context,
            )


async def menu_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not authorized(update, context):
        return

    query = update.callback_query

    if query is None:
        return

    try:
        await query.answer()
    except BadRequest as exc:
        logger.warning(
            "Ignoring stale callback query: %s",
            exc,
        )

    data = query.data

    if data is None:
        return

    try:
        if data in _MAIN_ACTIONS:
            await _handle_main_action(
                data,
                query,
                context,
            )

        elif data in _IMAGE_ACTIONS:
            await _handle_image_action(
                data,
                query,
                context,
            )

        elif (
                data in _EVENT_ACTIONS
                or data.startswith("events_page:")
                or data.startswith("event:")
        ):
            await _handle_event_action(
                data,
                query,
                context,
            )

        elif data in _SERVICE_ACTIONS:
            await _handle_service_action(
                data,
                query,
                context,
            )

        elif data in _STORAGE_ACTIONS:
            await _handle_storage_action(
                data,
                query,
                context,
            )

        elif data in _MANUAL_ACTIONS:
            await _handle_manual_action(
                data,
                query,
                context,
            )

        else:
            logger.warning(
                "Unhandled Telegram callback: %s",
                data,
            )

    except RuntimeCommandError as error:
        logger.warning(
            "Telegram runtime command failed: %s",
            error,
        )

        await query.edit_message_text(
            "⚠ BirdPi Runtime unavailable\n\n"
            "The BirdPi service is currently not reachable.",
            reply_markup=main_menu(),
        )

    except ServiceControlError as error:
        logger.warning(
            "Telegram service control failed: %s",
            error,
        )

        await query.edit_message_text(
            "⚠ Service control failed\n\n"
            "BirdPi could not perform the requested service action.",
            reply_markup=main_menu(),
        )
