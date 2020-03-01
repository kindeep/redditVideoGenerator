from clips import *

clips = []

for _ in range(0,3):
    clips.append(gen_transition_clip())

concatenate_videoclips(clips).to_videofile('temp/static.mp4')
