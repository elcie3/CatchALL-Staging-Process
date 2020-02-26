'''Usage:
python trim_moviepy.py --vidname ch0X_XX-XX-XX.XX --camerano cameraX
python trim_moviepy.py --vidname ch02_05-30-06.04 --camerano camera2
'''
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import subprocess 
import os
import argparse
import math
import time

parser = argparse.ArgumentParser(description='Trimming Training Videos to One Minute Video')
parser.add_argument('--vidname', type=str, help='basename of video')
parser.add_argument('--camerano', type=str, help='camera number')
args = parser.parse_args()

start_time = time.time()
vid_name = args.vidname
camera_no = args.camerano

vid_path = 'vid/{}/{}.mp4'.format(camera_no,vid_name)

trim_folder = 'trim/{}/{}'.format(camera_no,vid_name)
if not os.path.exists(trim_folder):
    os.makedirs(trim_folder)

print(vid_name,vid_path,trim_folder)

def get_duration(file):
    """Get the duration of a video using ffprobe."""
    cmd = 'ffprobe -i {} -show_entries format=duration -v quiet -of csv="p=0"'.format(file)
    output = subprocess.check_output(
        cmd,
        shell=True, # Let this run in the shell
        stderr=subprocess.STDOUT
    )
    # return round(float(output))  # ugly, but rounds your seconds up or down
    return float(output)
length = get_duration(vid_path)
tot_vid = math.ceil(length/60)
# ffmpeg_extract_subclip("full.mp4", start_seconds, end_seconds, targetname="cut.mp4")
for num_vid in range(0,tot_vid):
    trim_name = '{}/{}-{}.mp4'.format(trim_folder,vid_name,num_vid+1)
    if num_vid != tot_vid:
        start_sec = (60 * num_vid)
        end_sec = 60 * (num_vid+1)
    else:
        start_sec = end_sec + 1
        end_sec = length
    ffmpeg_extract_subclip(vid_path, start_sec, end_sec, targetname=trim_name)
    print(trim_name, start_sec, end_sec)
    print(time.time()-start_time)
