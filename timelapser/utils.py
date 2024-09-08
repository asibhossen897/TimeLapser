import datetime
import time
from rich.console import Console
from rich.panel import Panel

console = Console()


def find_time():
    x = datetime.datetime.now()
    date_for_name = (
        x.strftime("%d")
        + "-"
        + x.strftime("%m")
        + "-"
        + x.strftime("%Y")
        + "-"
        + x.strftime("%H")
        + "-"
        + x.strftime("%M")
        + "-"
        + x.strftime("%S")
    )
    return date_for_name


def display_timer(console, elapsed_time):
    elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    console.print(
        f"[bold yellow]Elapsed Time:[/bold yellow] [bold green]{elapsed_time_str}[/bold green]",
        end="\r",
    )


def result_format(mp4: bool):
    return ".mp4" if mp4 else ".avi"


def result_format_codec(mp4: bool):
    return "mp4v" if mp4 else "XVID"


def colorize_text(text: str, color: str = "green", style: str = "bold"):
    colored_text = f"[{style} {color}]{text}[/{style} {color}]"
    return colored_text


def rich_panel(
    text: str,
    title: str,
    border_style: str = "bold green",
    subtitle: str | None = None,
    style: str = "green",
):
    panel = Panel(
        text, title=title, border_style=border_style, subtitle=subtitle, style=style
    )
    return panel
