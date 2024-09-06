import typer
import datetime
import numpy as np
import cv2 as cv
import mss
import os
import time
from pynput import keyboard
from rich import print
from rich.table import Table
from rich.panel import Panel
from rich.console import Console


app = typer.Typer()
console = Console()


output_dir = "Outputs"
start_time = time.time()

if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# Find the time for name
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


# Determine video format
def result_format(mp4: bool):
    return ".mp4" if mp4 else ".avi"


def result_format_codec(mp4: bool):
    return "MP4V" if mp4 else "XVID"


# Start recording the video
def create_video(fps: int, mp4: bool, screen_size, output_dir: str = "Outputs"):
    fourcc = cv.VideoWriter_fourcc(*result_format_codec(mp4))
    file_path = f"{output_dir}/FrameRecorder_{find_time()}{result_format(mp4)}"
    out = cv.VideoWriter(
        file_path,
        fourcc,
        fps,
        screen_size,
    )
    return out, file_path


def record(out, monitor):
    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)

        # Check if the image has an alpha channel
        if frame.shape[2] == 4:
            # Remove the alpha channel by selecting only the RGB channels
            frame = frame[:, :, :3]

        # Convert from RGB to BGR if needed (OpenCV uses BGR format)
        # frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

        # Display the image (for testing purposes)
        # cv.imshow("Recording", frame)
        # cv.waitKey(1)  # Display the image for 1 ms

        out.write(frame)


# Define a global flag to stop recording
stop_recording = False


def on_press(key):
    global stop_recording
    try:
        if key.char == "Q":
            stop_recording = True
    except AttributeError:
        pass


@app.command()
def start(
    fps: int = 100,
    mp4: bool = True,
    monitor_index: int = 0,
    output_dir: str = "Outputs",
):
    """
    Start recording from the selected monitor.

    Args:
    fps: Frames per second for the video.
    mp4: If set to True, the video will be saved in .mp4 format, else .avi.
    monitor_index: Index of the monitor to record from. Default is monitor 0.
    """
    monitors = mss.mss().monitors

    # Check if monitor_index is valid
    if monitor_index < 0 or monitor_index >= len(monitors):
        typer.echo("Invalid monitor index. Please provide a valid index.")
        raise typer.Exit()

    selected_monitor = monitors[monitor_index]
    screen_size = (selected_monitor["width"], selected_monitor["height"])
    out, file_path = create_video(fps, mp4, screen_size, output_dir)

    print(
        Panel(
            f"[bold green]Recording from: [/bold green][bold magenta]{monitor_index}[/bold magenta]\n[bold red]Press 'Q' to stop recording![/bold red]",
            border_style="bold green",
            title="Recording Status",
            style="green",
        )
    )

    # Set up the keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Record the start time
    start_time = time.time()

    # Main recording loop
    while not stop_recording:
        current_time = time.time()
        elapsed_time = current_time - start_time
        display_timer(console, elapsed_time)

        record(out, selected_monitor)

        # Add a small delay to avoid high CPU usage
        time.sleep(0.1)

    listener.stop()
    out.release()

    # Clear the timer display line
    console.print(" " * 50, end="\r")

    print(
        Panel(
            f"[bold green]Recording finished and saved.[/bold green]\n[bold magenta]File saved at: {file_path}[/bold magenta]",
            border_style="bold green",
            title="Recording Status",
            subtitle="File saved successfully",
            style="green",
        )
    )


@app.command()
def list_monitors():
    """
    List all available monitors and their sizes.
    """
    monitors = mss.mss().monitors
    table = Table(title="Available Monitors", width=50, show_lines=True)

    table.add_column("Monitor", justify="center", style="cyan", no_wrap=True)
    table.add_column("Resolution", justify="center", style="magenta")

    for i, monitor in enumerate(monitors):
        width = monitor["width"]
        height = monitor["height"]
        table.add_row(f"{i}", f"{width}x{height}")

    print(table)


if __name__ == "__main__":
    app()
