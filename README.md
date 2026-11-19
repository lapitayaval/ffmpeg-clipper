# FFmpeg Video Clipper

A lightweight desktop GUI utility built with **Python** and **Tkinter** that simplifies extracting video clips and merging multiple MP4 files using **FFmpeg** and **FFprobe**—without having to retype complex command-line flags.

## Features

- **Fast Clip Extraction:** Select any `.mkv`, `.mp4`, `.avi`, or `.mov` file and extract segments using `HH:MM:SS` start and end timestamps.
- **Automatic English Stream Detection:** Uses `ffprobe` to inspect stream metadata and automatically select English audio and subtitle tracks (`eng`), falling back safely to default streams when unavailable.
- **Standardized Compatibility Encoding:** Converts clips into universally playable MP4 files (`libx264` video with `yuv420p`, stereo `AAC` audio, and `mov_text` subtitles) while stripping extraneous title metadata.
- **Multi-Clip Concatenation:** Select multiple MP4 clips at once to merge them losslessly (`-c copy`) via FFmpeg's `concat` demuxer, automatically generating and cleaning up the temporary file list (`join.txt`).
- **Safe File Handling:** Sanitizes timestamps in output filenames, auto-increments merged filenames (`merged_video_1.mp4`, etc.) to prevent accidental overwrites, and removes empty output files if an FFmpeg error occurs.

## Prerequisites

- **Python 3.x** (uses standard library modules: `tkinter`, `subprocess`, `os`)
- **FFmpeg & FFprobe** installed and available in your system `PATH`

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/lapitayaval/ffmpeg-clipper.git
   cd ffmpeg-clipper
   ```

2. Run the application:
   ```bash
   python ffmpeg-clipper.py
   ```

3. **To create a clip:** Click **Browse** to select a video file, enter the **Start Time** and **End Time** (`HH:MM:SS`), and click **Create Clip**.
4. **To merge clips:** Click **Merge Multiple Clips**, select two or more `.mp4` files, and the tool will combine them into a single file.

> **Note:** Output clips are currently saved to `C:\Users\valmr\Videos\Clips\Temp` by default. Update the `save_dir` variable in `ffmpeg-clipper.py` if you want to customize the destination folder.