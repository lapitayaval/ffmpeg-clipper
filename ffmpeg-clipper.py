import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def check_english_track(filepath, stream_type):
    command = [
        "ffprobe", "-v", "error", 
        "-select_streams", stream_type, 
        "-show_entries", "stream_tags=language", 
        "-of", "csv=p=0", filepath
    ]
    try:
        # Prevents a black cmd window from flashing
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        result = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=creationflags)
        return "eng" in result.stdout.lower()
    except Exception:
        return False

def browse_file():
    filepath = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=(("Video Files", "*.mkv *.mp4 *.avi *.mov"), ("All Files", "*.*"))
    )
    if filepath:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, filepath)

def make_clip():
    input_file = input_entry.get()
    start_time = start_entry.get()
    end_time = end_entry.get()

    if not input_file or not start_time or not end_time:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    save_dir = r"C:\Users\valmr\Videos\Clips"
    os.makedirs(save_dir, exist_ok=True)
    
    clean_start = start_time.replace(":", "-").replace(".", "-")
    clean_end = end_time.replace(":", "-").replace(".", "-")
    output_file = os.path.join(save_dir, f"{base_name}_{clean_start}_to_{clean_end}.mp4")

    # Dynamically select tracks based on the ffprobe scan
    audio_map = "0:a:m:language:eng" if check_english_track(input_file, "a") else "0:a:0"
    sub_map = "0:s:m:language:eng" if check_english_track(input_file, "s") else "0:s:0?"

    command = [
        "ffmpeg", "-y",
        "-ss", start_time,
        "-to", end_time,
        "-i", input_file,
        "-map", "0:v:0",
        "-map", audio_map,
        "-map", sub_map,
        "-metadata", "title=",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-ac", "2",
        "-c:s", "mov_text",
        output_file
    ]

    try:
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        subprocess.run(command, check=True, creationflags=creationflags)
        messagebox.showinfo("Success", f"Clip saved as:\n{output_file}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "FFmpeg failed. Check your timestamps or video file.")
        # Automatically clean up the broken 0-byte file
        if os.path.exists(output_file) and os.path.getsize(output_file) == 0:
            os.remove(output_file)
    except FileNotFoundError:
         messagebox.showerror("Error", "FFmpeg not found. Ensure it is installed.")

# --- GUI Setup ---
root = tk.Tk()
root.title("FFmpeg Video Clipper")
root.geometry("450x250")
root.eval('tk::PlaceWindow . center')

tk.Label(root, text="Input Video File:").pack(pady=(10, 0))
input_frame = tk.Frame(root)
input_frame.pack(pady=5)
input_entry = tk.Entry(input_frame, width=40)
input_entry.pack(side=tk.LEFT, padx=(0, 5))
tk.Button(input_frame, text="Browse", command=browse_file).pack(side=tk.LEFT)

tk.Label(root, text="Start Time (HH:MM:SS):").pack()
start_entry = tk.Entry(root, width=15)
start_entry.pack(pady=5)

tk.Label(root, text="End Time (HH:MM:SS):").pack()
end_entry = tk.Entry(root, width=15)
end_entry.pack(pady=5)

tk.Button(root, text="Create Clip", bg="green", fg="white", command=make_clip).pack(pady=15)

root.mainloop()