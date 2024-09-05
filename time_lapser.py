import os
import time
import typer
import cv2
import numpy as np
import pyautogui
import keyboard  # Library to capture key press events
import pygetwindow as gw  # Library for window handling

app = typer.Typer()


def capture_monitor_area(monitor_number: int = 0):
    """
    Capture a screenshot of the specified monitor area using PyAutoGUI.
    """
    screen_width, screen_height = pyautogui.size()
    monitors = pyautogui.getWindows()  # Get all monitors if you have multiple screens
    if len(monitors) > monitor_number:
        window = monitors[monitor_number]
        img = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        return np.array(img)
    else:
        return np.array(pyautogui.screenshot())  # Fall back to the default monitor


def capture_window(window_title: str):
    """
    Capture a screenshot of a specific window by its title.
    """
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        if window.isMinimized:
            window.restore()
        img = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        return np.array(img)
    except IndexError:
        typer.echo(f"Window '{window_title}' not found!")
        return None


@app.command()
def record(interval: int = 5, output_dir: str = "frames", monitor: int = 0, window_title: str = None,
           nonstop: bool = False):
    """
    Record screenshots periodically with multi-monitor or window support.

    - `monitor`: specify which monitor to capture (default is 0 for the primary monitor).
    - `window_title`: capture only a specific window by title (if specified).
    - `nonstop`: keep recording until "q" is pressed.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame_num = 0  # Counter for frame numbering
    typer.echo(f"Recording started. Press 'q' to stop (nonstop mode).")

    if nonstop:
        while True:
            if window_title:
                img = capture_window(window_title)  # Capture specific window
            else:
                img = capture_monitor_area(monitor)  # Capture monitor area

            if img is not None:
                # Save the screenshot as PNG
                cv2.imwrite(os.path.join(output_dir, f"frame_{frame_num:04d}.png"),
                            cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                typer.echo(f"Captured frame {frame_num + 1}")
                frame_num += 1
                time.sleep(interval)

            # Check if "q" has been pressed to stop recording
            if keyboard.is_pressed("q"):
                typer.echo("Recording stopped by user.")
                break
    else:
        # Time-bound recording
        duration = 60  # You can make this configurable
        total_frames = int(duration // interval)
        for frame_num in range(total_frames):
            if window_title:
                img = capture_window(window_title)
            else:
                img = capture_monitor_area(monitor)

            if img is not None:
                cv2.imwrite(os.path.join(output_dir, f"frame_{frame_num:04d}.png"),
                            cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                typer.echo(f"Captured frame {frame_num + 1}")
                time.sleep(interval)

    typer.echo(f"Recording finished. Frames saved to {output_dir}.")

    # Create video immediately after recording
    create_video(input_dir=output_dir, output_file="timelapse.avi", fps=10)


@app.command()
def create_video(input_dir: str = "frames", output_file: str = "timelapse.avi", fps: int = 10):
    """
    Convert captured frames into a timelapse video.
    """
    frame_files = sorted([os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".png")])

    if not frame_files:
        typer.echo(f"No frames found in directory {input_dir}!")
        return

    # Get the size of the first frame to set video dimensions
    first_frame = cv2.imread(frame_files[0])
    height, width, layers = first_frame.shape
    video = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

    typer.echo(f"Creating timelapse video from frames in {input_dir}...")

    for frame_file in frame_files:
        frame = cv2.imread(frame_file)
        video.write(frame)

    video.release()
    typer.echo(f"Video saved to {output_file}.")


if __name__ == "__main__":
    app()
