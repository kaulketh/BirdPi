"""
Telegram texts and messages for BirdPi..
"""
from telegram.ext import ContextTypes


def build_storage_text(
        context: ContextTypes.DEFAULT_TYPE,
) -> str:
    storage = context.application.bot_data["storage"]
    config = context.application.bot_data["config"]

    disk = storage.disk_usage()

    return (
        "💾 BirdPi Storage\n\n"
        f"Total: {disk['total_gib']:.1f} GiB\n"
        f"Used: {disk['used_gib']:.1f} GiB\n"
        f"Free: {disk['free_gib']:.1f} GiB "
        f"({disk['free_percent']:.1f} %)\n\n"
        f"Cleanup starts below: "
        f"{config.storage_min_free_percent:.0f} % free\n"
        f"Cleanup target: "
        f"{config.storage_target_free_percent:.0f} % free"
    )


def build_status_text(
        context: ContextTypes.DEFAULT_TYPE,
) -> str:
    storage = context.application.bot_data["storage"]
    runtime_status = context.application.bot_data["runtime_status"]
    service = context.application.bot_data["service"]

    state = runtime_status.read()
    disk = storage.disk_usage()

    return (
        "🐦 BirdPi Status\n\n"
        f"Service: {'RUNNING' if service.running() else 'STOPPED'}\n"
        f"Mode: {state.mode.upper()}\n"
        f"IR: {state.ir_mode.upper()}\n"
        f"Motion: {'ACTIVE' if state.motion_active else 'IDLE'}\n"
        f"Camera: {state.camera_model}\n"
        f"Resolution: {state.camera_resolution}\n"
        f"Free storage: {disk['free_gib']:.1f} GiB "
        f"({disk['free_percent']:.1f} %)"
    )


def build_service_text(
        context: ContextTypes.DEFAULT_TYPE,
) -> str:
    service = context.application.bot_data["service"]

    return (
        "⚙ BirdPi Service\n\n"
        f"Status: "
        f"{'RUNNING' if service.running() else 'STOPPED'}"
    )


def build_event_text(
        event,
) -> str:
    duration = (
        (event.ended_at - event.started_at).total_seconds()
        if event.ended_at
        else None
    )

    return (
        "🕊 Latest Event\n\n"
        f"ID: {event.id}\n"
        f"Started: {event.started_at.strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"Duration: "
        f"{f'{duration:.1f} s' if duration is not None else 'active'}\n"
        f"Images: {len(event.images)}\n"
        f"Video: {'yes' if event.video_filename else 'no'}"
    )


def build_manual_control_text(
        context: ContextTypes.DEFAULT_TYPE,
) -> str:
    runtime_status = context.application.bot_data[
        "runtime_status"
    ]

    status = runtime_status.read()

    return (
        "🛠 BirdPi Manual Control\n\n"
        f"Video: "
        f"{'RECORDING' if status.manual_video_active else 'IDLE'}\n"
        f"IR: {status.ir_mode.upper()}"
    )
