import moviepy.editor as mp
import numpy as np
import sys
import os
import cv2
from datetime import timedelta

def calc_video_length_in_seconds(user_input_video):
    # create video capture object
    data = cv2.VideoCapture(user_input_video)
    
    # count the number of frames
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv2.CAP_PROP_FPS)
    
    # calculate duration of the video
    video_time_seconds = round(frames / fps)
    #video_time = datetime.timedelta(seconds=video_time_seconds)
    #print(f"duration in seconds: {video_time_seconds}")
    #print(f"video time: {video_time}")   
    return video_time_seconds

def get_svg_values(fileName):
    f = open(fileName, 'r+')
    my_file_data = f.read()
    f.close()
    
    # clean up data
    # remove the leading M from our data
    # remove all C curves from data
    return np.array(my_file_data.replace("M ","").replace("C ","").replace(' ',',').split(','),dtype=np.float32).reshape(-1,2)
     
def compute_segments(svg_values, video_total_time, user_input_clipthreshold):
    
    # this should be 1000, but grab the final X coord just in case
    end_cord, _ = svg_values[len(svg_values)-1]
    seconds_delta = round(video_total_time / end_cord)

    segments = []
    start_clip = 0.0
    stop_clip = 0.0
    total_clip_time = 0.0

    for xseconds, ythreshold in svg_values:
        if ythreshold <= user_input_clipthreshold and start_clip == 0.0: # if the threshold is less than the user input and we haven't set the start yet, set it to xseconds
            start_clip = xseconds * seconds_delta
        elif ythreshold > user_input_clipthreshold and start_clip != 0.0: # if the threshold is greater than the user input and we have set the start yet, set the stop to xseconds
            stop_clip = xseconds * seconds_delta
            start_clip_datetime = str(timedelta(seconds=start_clip))
            stop_clip_datetime = str(timedelta(seconds=stop_clip))
            segments.append((start_clip_datetime, stop_clip_datetime)) # append the start and stop to the segemnts list
            total_clip_time = total_clip_time + (stop_clip - start_clip)
            start_clip = 0.0 # set values back to None
            stop_clip = 0.0

    return segments, total_clip_time

def create_cliped_vlideo(segments, user_input_video, video_title):
    video = mp.VideoFileClip(user_input_video)
    clips = []  # list of all video fragments
    for start_seconds, end_seconds in segments:
        # crop a video clip and add it to list
        c = video.subclip(start_seconds, end_seconds)
        clips.append(c)

    final_clip = mp.concatenate_videoclips(clips)
    final_clip.write_videofile(video_title+".mp4")
    final_clip.close()

np.set_printoptions(precision=1)
# user_input_video = input("Enter the path of your video: ")
user_input_video = "C:/Users/rmaca/Downloads/videoplayback.mp4"
assert os.path.exists(user_input_video), "I did not find the file at, "+str(user_input_video)

user_input_heatmap = input("Enter the path of your svg data: ")
assert os.path.exists(user_input_heatmap), "I did not find the file at, "+str(user_input_heatmap)
#user_input_clipthreshold = 70
      

 
video_total_time = calc_video_length_in_seconds(user_input_video)

svg_values = get_svg_values(user_input_heatmap)

while True:
    try:
         user_input_clipthreshold = int(input("Enter a clip threshold to determine the timestamps(ex. 1 being the highest and 100 the lowest, 70 is a good place to start): "))
    except ValueError:
        print("Please enter a valid threshold")
        continue
    
    segments, total_clip_time = compute_segments(svg_values, video_total_time, user_input_clipthreshold)
    print(f"Here are the computed timestamps (start, stop) based on the threshold {user_input_clipthreshold}: {segments}")
    duration = timedelta(seconds=total_clip_time)
    print(f"The total cliped video time will be: {duration}")
    
    confirm_clip = input("Enter Y to confirm or any input to enter a new threshold: ")
    
    if confirm_clip.casefold() == "Y".casefold():
        break
    else:
        continue 

user_input_title = input("Enter a title for your video: ")
create_cliped_vlideo(segments, user_input_video, user_input_title)