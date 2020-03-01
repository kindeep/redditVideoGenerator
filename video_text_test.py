from clips import *

clips = []
clips.append(create_comment_clip(author="adsf", content="Why is wrong with this?"))

video = concatenate_videoclips(clips)

video.write_videofile("media/test_out.mp4", fps=24)
