"""
Telegram handlers for BirdPi.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from birdpi.telegram.keyboard import (
    confirm_clear_images,
    confirm_clear_videos,
    confirm_service_restart,
    confirm_service_stop,
    event_menu,
    events_menu,
    main_menu,
    service_menu,
    storage_menu,
    confirm_delete_event_image,
    confirm_delete_event_video,
    confirm_delete_latest_image,
    latest_image_menu,
    manual_control_menu,
)
from birdpi.telegram.messages import (
    build_event_text,
    build_service_text,
    build_status_text,
    build_storage_text,

)


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

    await update.message.reply_text(
        build_status_text(context)
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

    page_size = 5

    all_events = storage.events()

    start = page * page_size
    end = start + page_size

    events = all_events[start:end]

    if not events and page > 0:
        page -= 1

        start = page * page_size
        end = start + page_size

        events = all_events[start:end]

    has_previous = page > 0
    has_next = end < len(all_events)

    await query.edit_message_text(
        f"📚 Events — Page {page + 1}",
        reply_markup=events_menu(
            events=events,
            page=page,
            has_previous=has_previous,
            has_next=has_next,
        ),
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

    match query.data:

        # main section
        case "main_menu":
            await query.edit_message_text(
                "🐦 BirdPi",
                reply_markup=main_menu(),
            )

        case "status":
            await query.message.reply_text(
                build_status_text(context)
            )

        # image actions
        case "latest_image":
            storage = context.application.bot_data["storage"]

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

        case "latest_image_delete":
            await query.edit_message_caption(
                "⚠ Delete latest image?",
                reply_markup=confirm_delete_latest_image(),
            )

        case "confirm_latest_image_delete":
            storage = context.application.bot_data["storage"]

            filename = context.application.bot_data.get(
                "selected_image_filename"
            )

            if filename is None:
                return

            deleted = storage.delete_image(
                filename
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

        # event actions
        case "latest_event":
            storage = context.application.bot_data["storage"]

            events = storage.events()

            if not events:
                await query.edit_message_text(
                    "🕊 No events available.",
                    reply_markup=main_menu(),
                )
                return

            event = events[0]

            context.application.bot_data["selected_event_id"] = event.id

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

        case data if data.startswith("events_page:"):
            page = int(
                data.removeprefix("events_page:")
            )

            await show_events_page(
                query,
                context,
                page=page,
            )

        case data if data.startswith("event:"):
            storage = context.application.bot_data["storage"]

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

        case "event_send_image":
            storage = context.application.bot_data["storage"]
            event_id = context.application.bot_data.get("selected_event_id")

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

        case "event_send_video":
            storage = context.application.bot_data["storage"]
            event_id = context.application.bot_data.get("selected_event_id")

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
            storage = context.application.bot_data["storage"]
            event_id = context.application.bot_data.get("selected_event_id")

            if event_id is None:
                return

            event = storage.event(event_id)

            if event is None or not event.images:
                await query.answer(
                    "No image available.",
                    show_alert=True,
                )
                return

            storage.delete_image(
                event.images[0].filename
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
            storage = context.application.bot_data["storage"]
            event_id = context.application.bot_data.get("selected_event_id")

            if event_id is None:
                return

            event = storage.event(event_id)

            if event is None or not event.video_filename:
                await query.answer(
                    "No video available.",
                    show_alert=True,
                )
                return

            storage.delete_video(
                event.video_filename
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

        # service control
        case "service":
            service = context.application.bot_data["service"]

            await query.edit_message_text(
                build_service_text(context),
                reply_markup=service_menu(
                    service.running()
                ),
            )

        case "service_start":
            service = context.application.bot_data["service"]
            service.start()

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
            service = context.application.bot_data["service"]
            service.stop()

            await query.edit_message_text(
                build_service_text(context),
                reply_markup=service_menu(
                    service.running()
                ),
            )

        case "confirm_service_restart":
            service = context.application.bot_data["service"]
            service.restart()

            await query.edit_message_text(
                "⚙ BirdPi Service\n\n"
                "Restart completed.",
                reply_markup=service_menu(
                    service.running()
                ),
            )

        # storage actions
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
            storage = context.application.bot_data["storage"]

            deleted = storage.clear_images()

            await query.edit_message_text(
                f"🗑 Deleted {deleted} image(s).",
                reply_markup=storage_menu(),
            )

        case "confirm_clear_videos":
            storage = context.application.bot_data["storage"]

            deleted = storage.clear_videos()

            await query.edit_message_text(
                f"🗑 Deleted {deleted} video(s).",
                reply_markup=storage_menu(),
            )

        # manual controls
        case "manual_control":
            runtime_status = context.application.bot_data[
                "runtime_status"
            ]

            status = runtime_status.read()

            await query.edit_message_text(
                "🛠 BirdPi Manual Control",
                reply_markup=manual_control_menu(
                    status.manual_video_active
                ),
            )

        case "manual_capture":
            runtime = context.application.bot_data["runtime"]

            response = await asyncio.to_thread(runtime.capture_image)

            await query.answer(
                response,
                show_alert=True,
            )

        case "manual_video_start":
            runtime = context.application.bot_data["runtime"]

            response = await asyncio.to_thread(runtime.video_start)

            await query.edit_message_text(
                f"🛠 BirdPi Manual Control\n\n{response}",
                reply_markup=manual_control_menu(
                    manual_video_active=True
                ),
            )

        case "manual_video_stop":
            runtime = context.application.bot_data["runtime"]

            response = await asyncio.to_thread(runtime.video_stop)

            await query.edit_message_text(
                f"🛠 BirdPi Manual Control\n\n{response}",
                reply_markup=manual_control_menu(
                    manual_video_active=False
                ),
            )

        case "manual_ir_off":
            runtime = context.application.bot_data["runtime"]
            response = await asyncio.to_thread(runtime.ir_off)

            await query.answer(
                response,
                show_alert=True,
            )

        case "manual_ir_left":
            runtime = context.application.bot_data["runtime"]
            response = await asyncio.to_thread(runtime.ir_left)

            await query.answer(
                response,
                show_alert=True,
            )

        case "manual_ir_right":
            runtime = context.application.bot_data["runtime"]
            response = await asyncio.to_thread(runtime.ir_right)

            await query.answer(
                response,
                show_alert=True,
            )

        case "manual_ir_both":
            runtime = context.application.bot_data["runtime"]
            response = await asyncio.to_thread(runtime.ir_both)

            await query.answer(
                response,
                show_alert=True,
            )
