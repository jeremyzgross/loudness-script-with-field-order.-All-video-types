import os
import shutil
import ffmpeg
import pyloudnorm as pyln
import soundfile as sf
import moviepy.editor as mp
import tkinter as tk
from tkinter import filedialog

# setting a field that points to ffmpeg (a library)
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"

BASE_PATH = '/Users/jeremyzgross/Downloads/BLACKSPOT QC/TEST VIDEOS/'
mp3Folder = '/Users/jeremyzgross/Downloads/BLACKSPOT QC/EXPORTED MP3s/'

# Create Good Videos Folder
# Create Bad Videos folder
# Identify folder for videos to be tested




#converts video files to sound only files (mp3s)

def measure_loudness():
    badframerateCounter = 0

    #for loop that through a directory in your OS. Replace the directory in the () to where your video files are located.
    for filename in os.listdir(BASE_PATH):
        if filename.endswith(".mp4"):
            sourceMp4Path = BASE_PATH + os.path.splitext(filename)[0] + '.mp4'
            print(sourceMp4Path)
        elif filename.endswith(".mov"):
            sourceMp4Path = BASE_PATH + os.path.splitext(filename)[0] + '.mov'
            print(sourceMp4Path)
        elif filename.endswith(".mxf"):
            sourceMp4Path = BASE_PATH + os.path.splitext(filename)[0] + '.mxf'
            print(sourceMp4Path)
        else:
            continue
        #use ffmpeg to probe the video file and extract metadata
        probe = ffmpeg.probe(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/TEST VIDEOS/{filename}')
        video_stream= next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            continue #skips files without video stream

        frame_rate = video_stream.get('r_frame_rate')
        field_order = video_stream.get('field_order')
        print(f'Frame rate: {frame_rate}')
        print(f'Field order: {field_order}')
        if frame_rate == '24000/1001' and field_order == 'progressive':
            shutil.move(sourceMp4Path,f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS')
        elif frame_rate == '30000/1001' and field_order == 'tb':
            shutil.move(sourceMp4Path, f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS')
        else:
            shutil.move(sourceMp4Path, f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/BAD VIDEOS')
            badframerateCounter += 1
# use moviepy to load video file into 'clip' variable. Replace the directory in the () to where
# to where your video files are locate bewtween f and {filename}. Make sure there is a / at the end of your directory

    for filename in os.listdir(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS'):
        if not filename.endswith('.mp4') and not filename.endswith('.mov'):
            continue
        clip = mp.VideoFileClip(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS/{filename}')
        # removes extension from file name before converting
        noext = os.path.splitext(filename) [0]
        print(f'noext {noext}')
        print(f'writing file')
        # creates mp3 file. Replace the directory with where the converted video to audio file will be placed bewtween F and {noext}
        clip.audio.write_audiofile(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/EXPORTED MP3s/{noext}.mp3')

    for filename in os.listdir(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/BAD VIDEOS'):
        if not filename.endswith('.mp4') and not filename.endswith('.mov'):
            continue
        clip = mp.VideoFileClip(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/BAD VIDEOS/{filename}')
        # removes extension from file name before converting
        noext = os.path.splitext(filename) [0]
        print(f'noext {noext}')
        print(f'writing file')
        # creates mp3 file. Replace the directory with where the converted video to audio file will be placed bewtween F and {noext}
        clip.audio.write_audiofile(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/EXPORTED MP3s/{noext}.mp3')


# for loop that measures loudness. converted video to audio file are placed
    loud_files = 0
    for filename in os.listdir(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/EXPORTED MP3s'):
        if not filename.endswith(".mp3"):
            continue
        data, rate = sf.read(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/EXPORTED MP3s/{filename}')
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(data)
        sourceMp4Path = '/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS/' + os.path.splitext(filename)[
            0] + '.mov'
        if loudness>=-22 or loudness <= -26:
            shutil.move(sourceMp4Path, f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/BAD VIDEOS')
            loud_files += 1
        else:
            print(f'{filename} does not need to be moved.')

        print(filename)
        print('loudness')
        print(loudness)
    print(str(loud_files) + " LOUD FILES")
    print(f'Number of videos with bad frame rate and/or field order: {badframerateCounter}')


 # Clear files in the MP3 folder
    for filename in os.listdir(mp3Folder):
        file_path = os.path.join(mp3Folder, filename)
        try:
            if filename.endswith(".mp3"):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


    # # Move files back into TEST VIDEO folder for testing
    # Good_videos_source = os.path.join(BASE_PATH, 'GOOD VIDEOS')
    # Bad_videos_source = os.path.join(BASE_PATH, 'BAD VIDEOS')
    # original_videos = os.path.join(BASE_PATH, 'TEST VIDEOS')
    #
    # allgoodfiles = os.listdir(Good_videos_source)
    # allbadfiles = os.listdir(Bad_videos_source)
    #
    # for f in allgoodfiles:
    #     src_path = os.path.join(Good_videos_source, f)
    #     dst_path = os.path.join(original_videos, f)
    #     shutil.move(src_path, dst_path)
    #
    # for f in allbadfiles:
    #     src_path_2 = os.path.join(Bad_videos_source, f)
    #     dst_path = os.path.join(original_videos, f)
    #     shutil.move(src_path_2, dst_path)


if __name__ == '__main__':
    measure_loudness()