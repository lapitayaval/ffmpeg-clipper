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
    save_dir = os.path.join(os.path.expanduser("~"), "Videos", "Clips")
    os.makedirs(save_dir, exist_ok=True)
    
    clean_start = start_time.replace(":", "-").replace(".", "-")
    clean_end = end_time.replace(":", "-").replace(".", "-")
    output_file = os.path.join(save_dir, f"{base_name}_{clean_start}_to_{clean_end}.mp4")

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
        if os.path.exists(output_file) and os.path.getsize(output_file) == 0:
            os.remove(output_file)
    except FileNotFoundError:
         messagebox.showerror("Error", "FFmpeg not found. Ensure it is installed.")

def merge_clips():
    # Allow the user to select multiple files at once
    filepaths = filedialog.askopenfilenames(
        title="Select Clips to Merge (Hold CTRL to select multiple)",
        filetypes=(("MP4 Files", "*.mp4"), ("All Files", "*.*"))
    )
    
    if len(filepaths) < 2:
        if filepaths:  # Only show error if they selected 1 file (if 0, they just cancelled)
            messagebox.showwarning("Warning", "Please select at least two clips to merge.")
        return

    save_dir = save_dir = os.path.join(os.path.expanduser("~"), "Videos", "Clips")
    os.makedirs(save_dir, exist_ok=True)
    
    # Auto-increment the filename to prevent overwriting older merges
    output_file = os.path.join(save_dir, "merged_video.mp4")
    counter = 1
    while os.path.exists(output_file):
        output_file = os.path.join(save_dir, f"merged_video_{counter}.mp4")
        counter += 1

    list_file_path = os.path.join(save_dir, "join.txt")

    # Generate the join.txt file programmatically
    with open(list_file_path, 'w', encoding='utf-8') as f:
        for path in filepaths:
            clean_path = path.replace('\\', '/')
            f.write(f"file '{clean_path}'\n")

    command = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file_path,
        "-c", "copy",
        output_file
    ]

    try:
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        subprocess.run(command, check=True, creationflags=creationflags)
        os.remove(list_file_path)  # Clean up the text file automatically
        messagebox.showinfo("Success", f"Clips merged successfully into:\n{output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Merging failed.\n{e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("FFmpeg Video Clipper")
root.geometry("450x320")
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

tk.Button(root, text="Create Clip", bg="green", fg="white", command=make_clip).pack(pady=(15, 5))

# Visual separator
tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=20, pady=10)

tk.Button(root, text="Merge Multiple Clips", bg="blue", fg="white", command=merge_clips).pack(pady=5)

root.mainloop()