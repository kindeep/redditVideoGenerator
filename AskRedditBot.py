from AskReddit import gen_video_from_hot
import time

delay = 60 * 60 * 8

while True:
    gen_video_from_hot()
    time.sleep(delay)
