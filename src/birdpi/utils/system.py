"""
Utilities for system information.
"""
from pathlib import Path


def get_cpu_temperature() -> float:
    """
    Return CPU temperature in degrees Celsius.
    """

    temperature_file = Path("/sys/class/thermal/thermal_zone0/temp")
    temperature = int(temperature_file.read_text().strip())

    return temperature / 1000


def get_uptime() -> int:
    """
    Return system uptime in seconds.
    """

    uptime_file = Path("/proc/uptime")
    uptime_seconds = uptime_file.read_text().split()[0]

    return int(float(uptime_seconds))


def format_uptime(seconds: int) -> str:
    """
    Format uptime seconds as days, hours, and minutes.
    """

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    if days:
        return f"{days}d {hours}h {minutes}m"

    if hours:
        return f"{hours}h {minutes}m"

    return f"{minutes}m"
