import cv2, time, os
import moviepy.editor as mpy
import ffmpy
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import subprocess
import math

""" requirements
conda install -c conda-forge moviepy
or 
pip install moviepy

pip install ffmpy
"""

time_per_trim = 60

def get_fps(video):
    fps = video.get(cv2.CAP_PROP_FPS)

def trim_one_minute(video_path,dest):
    time_per_trim = 60
    duration = get_duration(video_path)
    number_of_vids = math.ceil(duration/60)
    print(number_of_vids)

    for vid_num in range(number_of_vids):
        trim(video_path,vid_num,dest)
    

def trim(vid_path, vid_num,dest):
    str_vid_num = f"{vid_num}"
    str_vid_num = str_vid_num.zfill(3)
    vid_name = gen_filename(vid_path)
    file_name = vid_name.split(".")[0]
    ffmpeg_extract_subclip(vid_path, vid_num*time_per_trim, (vid_num+1)*time_per_trim, targetname=f"{dest}\\{file_name}_{vid_num}.mp4")
    

def get_duration(file):
    """Get the duration of a video using ffprobe."""
    
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # return round(float(output))  # ugly, but rounds your seconds up or down

    output = float(result.stdout)
    print(f"duration = {output}")
    return output

def gen_filename(path):
    #return name in CATCHALL format 
    filename = path
    filename = filename.split("\\")
    filename = filename[len(filename)-1]
    extension = filename.split(".")
    extension = extension[len(extension)-1]
    return "ch"+"0"+filename[2:4]+"_"+filename[5:13]+"_"+filename[13:17]+"." +extension

def compress(input_name):
    
    crf = 24 #18 -24
    output_name = f"compressed_{input_name}"
    inp={input_name:None}
    outp = {output_name:'-vcodec libx264 -crf %d'%crf}
    ff=ffmpy.FFmpeg(inputs=inp,outputs=outp)
    print(ff.cmd) # just to verify that it produces the correct ffmpeg command
    ff.run()
    print("done compressing!")

def main():
    #get_duration("twice.mp4")
    #trim("twice.mp4",0)
    trim_one_minute("twice.mp4")

if __name__ == "__main__":
    main()