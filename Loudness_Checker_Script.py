import os
import shutil
import ffmpeg
import pyloudnorm as pyln
import soundfile as sf
import moviepy.editor as mp
import tkinter as tk
from tkinter import filedialog

os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"

BASE_PATH = ''
mp3Folder = ''

def select_base_path():
    root = tk.Tk()
    root.withdraw()
    base_path = filedialog.askdirectory(title="Select Base Path")
    if base_path:
        global BASE_PATH
        BASE_PATH = base_path
        create_folders(BASE_PATH)  # Pass the selected base path to create_folders
        sort_videos()
        print("Video files sorted into good and bad videos directories.")
    else:
        print("No base path selected.")

def create_folders(base_path):
    global mp3Folder
    mp3Folder = os.path.join(base_path, 'Exported MP3s')
    os.makedirs(mp3Folder, exist_ok=True)

    good_videos_folder = os.path.join(base_path, 'Good Videos')
    os.makedirs(good_videos_folder, exist_ok=True)

    bad_videos_folder = os.path.join(base_path, 'Bad Videos')
    os.makedirs(bad_videos_folder, exist_ok=True)

def sort_videos():
    badframerateCounter = 0

    for filename in os.listdir(BASE_PATH):
        if filename.endswith(".mp4"):
            sourceMp4Path = os.path.join(BASE_PATH, filename)
        elif filename.endswith(".mov"):
            sourceMp4Path = os.path.join(BASE_PATH, filename)
        elif filename.endswith(".mxf"):
            sourceMp4Path = os.path.join(BASE_PATH, filename)
        else:
            continue

        probe = ffmpeg.probe(os.path.join(BASE_PATH, filename))
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            continue

        frame_rate = video_stream.get('r_frame_rate')
        field_order = video_stream.get('field_order')
        print(f'Frame rate: {frame_rate}')
        print(f'Field order: {field_order}')

        if frame_rate == '24000/1001' and field_order == 'progressive':
            shutil.move(sourceMp4Path, os.path.join(BASE_PATH, 'Good Videos'))
        elif frame_rate == '30000/1001' and field_order == 'tb':
            shutil.move(sourceMp4Path, os.path.join(BASE_PATH, 'Good Videos'))
        else:
            shutil.move(sourceMp4Path, os.path.join(BASE_PATH, 'Bad Videos'))
            badframerateCounter += 1

    for filename in os.listdir(os.path.join(BASE_PATH, 'Good Videos')):
        if not filename.endswith('.mp4') and not filename.endswith('.mov'):
            continue
        clip = mp.VideoFileClip(os.path.join(BASE_PATH, 'Good Videos', filename))
        noext = os.path.splitext(filename)[0]
        print(f'noext {noext}')
        print(f'writing file')
        clip.audio.write_audiofile(os.path.join(mp3Folder, f'{noext}.mp3'))

    for filename in os.listdir(os.path.join(BASE_PATH, 'Bad Videos')):
        if not filename.endswith('.mp4') and not filename.endswith('.mov'):
            continue
        clip = mp.VideoFileClip(os.path.join(BASE_PATH, 'Bad Videos', filename))
        noext = os.path.splitext(filename)[0]
        print(f'noext {noext}')
        print(f'writing file')
        clip.audio.write_audiofile(os.path.join(mp3Folder, f'{noext}.mp3'))

    measure_loudness(badframerateCounter)

def measure_loudness(badframerateCounter):
    loud_files = 0

    for filename in os.listdir(mp3Folder):
        if not filename.endswith(".mp3"):
            continue
        data, rate = sf.read(os.path.join(mp3Folder, filename))
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(data)
        sourceMp4Path = os.path.join(BASE_PATH, 'Good Videos', os.path.splitext(filename)[0] + '.mov')
        if -26 >= loudness <= -22:
            shutil.move(sourceMp4Path, os.path.join(BASE_PATH, 'Bad Videos'))
            loud_files += 1
        else:
            print(f'{filename} does not need to be moved.')

        print(filename)
        print('loudness')
        print(loudness)
    print(str(loud_files) + " LOUD FILES")
    print(f'Number of videos with bad frame rate and/or field order: {badframerateCounter}')


if __name__ == "__main__":
    select_base_path()

    try:
        shutil.rmtree(mp3Folder)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (mp3Folder, e))