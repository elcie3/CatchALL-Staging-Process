# sudo apt install ffmpeg 
# pip install moviepy
# pip install opencv-python
# pip install ez_setup
"""above step required before installing gizeh"""
# pip install gizeh

"""
FOLDER STRUCTURE

- APMC_VIDEOS
--- ch01_00000
----- ch01_00000.mp4
----- ch01_00001.mp4
--- ch02_00000
----- ch02_00000.mp4
- Trimmed_APMC
--- ch01_00000
----- ch01_00000-1.mp4
----- ch01_00000-2.mp4
----- ch01_00000-3.mp4
----- ch01_00001-1.mp4
----- ch01_00001-2.mp4
----- ch01_00001-3.mp4
--- ch02_00000
----- ch02_00000-1.mp4
----- ch02_00000-2.mp4
"""


from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy
import subprocess
import os
import shutil
import argparse
import math
import time
import cv2
import pandas as pd
from glob import glob
import csv
import gizeh
import moviepy.editor as mpy

# import video_sort


"""
usage

python video_trim/video_trim.py --client test --duration 60

"""

parser = argparse.ArgumentParser(description='Trimming videos into n-seconds')
parser.add_argument('--client', type=str, help='Client name')
parser.add_argument('--duration', type=str, help='Trimmed video length in seconds')
parser.add_argument('--staging', type=str, help='Staging folder directory')
args = parser.parse_args()

client_name = args.client
trim_time = args.duration
staging = args.staging


def remove_folder_spaces(camera_list, vid_directory):
    """Remove the spaces from the folder names"""
    new_camera_list = []
    for camera in camera_list:
        camera_replaced = camera.replace(' ', '')
        new_camera_list.append(camera_replaced)
        if (camera_replaced != camera):
            orig_path = f'{vid_directory}/{camera}'
            new_path = f'{vid_directory}/{camera_replaced}'
            os.rename(orig_path, new_path)
    return new_camera_list


def remove_vidname_spaces(vid_list, vid_directory, camera):
    """Remove the spaces from the video names"""
    new_vidname_list = []
    for vid_path in vid_list:
        vid_replaced = vid_path.replace(' ', '')
        new_vidname_list.append(vid_replaced)
        if (vid_replaced != vid_path):
            old_vid = f'{vid_path}'
            new_vid = f'{vid_replaced}'
            os.rename(old_vid, new_vid)
    return new_vidname_list


def get_duration(vid_file, mpeg=False, fps=30): 
    """Get the duration of a video using ffprobe."""
    try:
        cmd = 'ffprobe -i {} -show_entries format=duration -v quiet -of csv="p=0"'.format(vid_file)
        output = subprocess.check_output(
            cmd,
            shell=True,  # Let this run in the shell
            stderr=subprocess.STDOUT
        )
        length = float(output)
        mpeg = True
    except:
        cap = cv2.VideoCapture(vid_file)
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
        if int(major_ver) < 3:
            fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        else:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        length = frame_count/fps
        mpeg = False
    return length, mpeg, fps


def trim_vid(data_folder, client_name, trim_time):
    trim_csv = f'{client_name}_Trimmed.csv'
    activity_csv = 'activity_log.csv'
    start_time = time.time()
    vid_directory = f'{data_folder}/{client_name}_Videos'
    camera_list = [x[1] for x in os.walk(vid_directory)]
    camera_list = remove_folder_spaces(camera_list[0], vid_directory)
    processed_videos = 0
    dropped_videos = 0
    File_Path = []
    Processed = []
    Timestamp = []
    File_Size = []
    Duration = []
    if os.path.exists(activity_csv):
        with open(activity_csv, 'r') as f:
            opened_file = f.readlines()
            var = opened_file[-1].split(',')[0]
            Process_ID = 1 + int(var)
    else:
        Process_ID = 0
    Process_Name = "Video Trim"
    Input_File_Path = vid_directory

    for camera in camera_list:
        trim_directory = f'{data_folder}/{client_name}_Trimmed/{camera}'
        Output_File_Path = trim_directory
        if not os.path.exists(trim_directory):
            os.makedirs(trim_directory)
        vid_list = glob(f'{vid_directory}/{camera}/*.mp4')
        vid_list = remove_vidname_spaces(vid_list, vid_directory, camera)
        # print(vid_list)
        for vid_path in vid_list:
            length, mpeg, fps = get_duration(vid_path)
            if mpeg:
                '''Duration'''
                tot_vid = math.ceil(length/60)
            else:
                '''Total frames'''
                tot_vid = math.ceil(length/(60*fps))

            vid_name = os.path.splitext(os.path.basename(vid_path))[0]
            for num_vid in range(0,tot_vid):
                int_num_vid = num_vid + 1
                trim_name = f'{trim_directory}/{vid_name}-{int_num_vid:03d}.mp4'
                if num_vid != tot_vid:
                    start_sec = (60 * num_vid)
                    end_sec = 60 * (num_vid+1)
                else:
                    start_sec = end_sec + 1
                    end_sec = length
                ffmpeg_extract_subclip(vid_path, start_sec, end_sec, targetname=trim_name)
                File_Path.append(trim_name)
                Timestamp.append(time.time())
                File_Size.append(os.path.getsize(trim_name)/1024)
                fps_t = get_duration(trim_name)
                Duration.append(fps_t[0])
                if fps_t[0] == 0.0:
                    os.remove(trim_name)
                    dropped_videos += 1
                    Processed.append('DROPPED')
                else:
                    Processed.append('DONE')
                processed_videos += 1
                print(f'FILE NAME: {trim_name}')
    processing_time = time.time()-start_time
    end_time = time.time()
    list_of_data = list(zip(File_Path, Processed, Timestamp, File_Size, Duration))
    # list_of_data2 = [Process_ID, Process_Name, Input_File_Path, Output_File_Path, start_time, end_time]
    # print(list_of_data2)
    data = pd.DataFrame(list_of_data, columns=["File_Path", "Processed", "Timestamp", "File_Size", "Duration"])
    with open(trim_csv, 'a') as f:
        data.to_csv(f, header=False, index=False)
    
    data2 = pd.DataFrame(columns=["Process_ID", "Process_Name", "Input_File_Path", "Output_File_Path", "Start_Time", "End_Time"])
    data2 = data2.append({
            "Process_ID": Process_ID,
            "Process_Name": Process_Name,
            "Input_File_Path": Input_File_Path,
            "Output_File_Path": Output_File_Path,
            "Start_Time": start_time,
            "End_Time": end_time}, ignore_index=True)
    print(data2)
    with open(activity_csv, 'a') as f:
        data2.to_csv(f, header=False, index=False)    
    print(f'PROCESSING TIME: {processing_time:.2f} seconds')
    print(f'NO OF PROCESSED VIDEOS: {processed_videos}')
    print(f'NO OF DROPPED VIDEOS: {dropped_videos}')


def delete_staging(stage_dest):
    shutil.rmtree(stage_dest)

def main():
    #do nothing for now
    something = 0
    #trim_vid('/catch-all', client_name, trim_time)

def new_trim_clip():
    myclip = mpy.VideoFileClip("try.mp4")
    myclip2 = myclip.subclip(0,30)
    myclip2.write_videofile("movie.mp4",fps=30)

new_trim_clip()