from moviepy.editor import *
import datetime as dt
import pandas as pd
import praw


def comment_html(username, content):
    str = "<!DOCTYPE html><html><head>" \
          "<style>body {background-color: rgb(26, 26, 27);color: white;font-family: BentonSans, sans-serif;}.username {color: rgb(79, 188, 255);}.content {padding: 5px}.header {padding: 0 0 0 5px}</style>" \
          "</head>" \
          "<body><div><div class = 'header'><span class=username>"+username + \
        "</span></div><div class = 'content'>" + content + "</div></div></body></html>"
    return str


def gen_comment_image(username, content, save_path):
    imgkit.from_string(comment_html(
        'kindeep', 'asdfasdfafg asgdfasdf sadgasdfewher sehagdsf'), save_path)


print("Subscribe or i'll end humanity.")

with open('reddit_secret.json') as f:
    secret = json.load(f)

reddit = praw.Reddit(client_id=secret['client_id'],
                        client_secret=secret['client_secret'],
                        user_agent=secret['user_agent'])

# print(reddit.read_only)

for a_subreddit in reddit.subreddits.popular(limit=1):
    print(a_subreddit.display_name, '\n' +
          ('=' * len(a_subreddit.display_name)))
    for submission in a_subreddit.top(limit=10):
        print(submission.title, '\n')


gen_comment_image("kindeep", "something", "media/test.png")
img_clip = ImageClip("media/test.png").set_duration(10)

imgs = ["media/test.png", "media/test.1.png"]

clips = [ImageClip(m).set_duration(2) for m in imgs]

concat_clip = concatenate_videoclips(clips, method="compose")
concat_clip.write_videofile("media/test.mp4", fps=24)
