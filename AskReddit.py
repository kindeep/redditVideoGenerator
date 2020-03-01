#!./venv/bin/python
import praw
from clips import *
from yt_upload import upload_video
from tinydb import TinyDB, Query
import json

db = TinyDB('log/db.json')
created_vids_db = db.table('created_videos')
uploaded_vids_db = db.table('uploaded_vids')

FPS = 30
BACKGROUND_TRACK_VOLUME = 0.12
DURATION: int = 60 * 5
DESCRIPTION = "Yes I'm an actual robot. \n"


def random_title_msg():
    return "Subscribe or I'll end humanity."


def write_to_log(text):
    f = open("ask_reddit_log.txt", "a+")
    f.write(text)
    f.close()


def check_video_in_db(url):
    vid = Query()
    # Search db for already created video
    found_val = uploaded_vids_db.search(vid.permanent_reddit_url == url)
    print(found_val)
    if len(found_val) > 0:
        return True
    else:
        return False


def prompt_create_submission_video(submission, save_path):
    if check_video_in_db(submission.permalink):
        valid_in = ['Y', 'y', 'N', 'n']
        choice = None
        while not valid_in.__contains__(choice):
            choice = input("Video already uploaded, do you still want to create the video? (Y/N): ")
        if not (choice == 'Y' or choice == 'y'):
            print("Okay, exiting.")
            return

        create_submission_video(submission, save_path)


def create_submission_video(submission, save_path):
    clips = []
    enm_imgs = 0
    curr_duration: int = 0
    TRANSITION_LEN = gen_transition_clip().duration
    clips.append(gen_intro_clip())
    clips.append(create_comment_clip(
        submission.author.name, "AskReddit: " + submission.title))
    clips.append(gen_transition_clip())
    clips.append(gen_title_message_clip(random_title_msg()))
    submission.sort = 'top'
    submission.comments.replace_more(limit=50)
    for comment in submission.comments:
        print("\nComment: ", comment.body if comment.body else "[deleted]")
        if not comment.body:
            continue
        temp = create_comment_clip(
            author=comment.author.name if comment.author else "[deleted]",
            content=comment.body if comment.body else "[deleted]")
        clips.append(gen_transition_clip())
        clips.append(temp)
        enm_imgs = enm_imgs + 1
        curr_duration = curr_duration + temp.duration + TRANSITION_LEN
        if curr_duration >= DURATION:
            break
        print(curr_duration)
    clips.append(gen_intro_clip())
    concat_clip = concatenate_videoclips(clips)
    background_audio = gen_background_audio_clip(
        concat_clip.duration).fx(volumex, BACKGROUND_TRACK_VOLUME)
    concat_clip.audio = CompositeAudioClip(
        [background_audio, concat_clip.audio])
    concat_clip.write_videofile(save_path, fps=FPS)
    created_vids_db.insert({'permanent_url': submission.permalink, 'url': submission.url})


def gen_video_from_hot():
    print("Subscribe or i'll end humanity.")

    with open('reddit_secret.json') as f:
        secret = json.load(f)

    print(secret)
    reddit = praw.Reddit(client_id=secret['client_id'],
                         client_secret=secret['client_secret'],
                         user_agent=secret['user_agent'])

    a_subreddit = reddit.subreddit('AskReddit')
    print(a_subreddit.display_name, '\n' + ('=' * len(a_subreddit.display_name)))
    submission = list(a_subreddit.hot(limit=1))[0]
    print("\nTitle:", submission.title)
    print("URL: " + submission.url)
    print("Author:", submission.author)
    print("\n")
    submission.sort = 'top'
    path = "rtemp" + ".mp4"
    create_submission_video(submission, path)
    uploaded = True
    upload_response = None
    try:
        upload_response = upload_video(path,
                                       description=DESCRIPTION + "Link to subreddit post: " + submission.url + "\n" +
                                                   submission.title, title="AskReddit: " +
                                                                           submission.title,
                                       keywords="AskReddit, Reddit")
    except:
        uploaded = False
    if uploaded:
        uploaded_vids_db.insert(
            {"reddit_url": submission.url, "permanent_reddit_url": submission.permalink,
             "youtube": upload_response})
    clean_temp()


def main():
    print("Subscribe or i'll end humanity.")

    with open('reddit_secret.json') as f:
        secret = json.load(f)

    reddit = praw.Reddit(client_id=secret.client_id,
                         client_secret=secret.client_secret,
                         user_agent=secret.user_agent)

    type = input("1. Top 2. Custom 3. Hot: ")

    if int(type) == 1:
        a_subreddit = reddit.subreddit('AskReddit')

        print(a_subreddit.display_name, '\n' + ('=' * len(a_subreddit.display_name)))

        for index, submission in enumerate(a_subreddit.top(limit=1)):
            print("\nTitle:", submission.title)
            print("Author:", submission.author)
            print("\n")
            submission.sort = 'top'
            path = "rtemp" + str(index) + ".mp4"
            prompt_create_submission_video(submission, path)
            uploaded = True
            upload_response = None
            try:
                upload_video(path, description="", title="AskReddit: " +
                                                         submission.title, keywords="AskReddit, Reddit")
            except:
                uploaded = False
            if uploaded:
                uploaded_vids_db.insert(
                    {"reddit_url": submission.url, "permanent_reddit_url": submission.permalink,
                     "youtube": upload_response})
            clean_temp()

    elif int(type) == 2:
        url = input("Enter subreddit submission url: ")
        submission = praw.models.Submission(reddit, url=url)
        print("\nTitle:", submission.title)
        print("Author:", submission.author)
        print("\n")
        submission.sort = 'top'
        path = "media/" + submission.title + "_" + submission.id + ".mp4"
        prompt_create_submission_video(submission, path)
        uploaded = True
        upload_response = None
        try:
            uploaded_respone = upload_video(path,
                                            description=DESCRIPTION + "Link to subreddit post: " + url + "\n" + submission.title,
                                            title="AskReddit: " + submission.title, keywords="AskReddit, Reddit")
        except:
            uploaded = False
        if uploaded:
            uploaded_vids_db.insert(
                {"reddit_url": url, "permanent_reddit_url": submission.permalink, "youtube": upload_response})

    elif int(type) == 3:
        a_subreddit = reddit.subreddit('AskReddit')
        print(a_subreddit.display_name, '\n' + ('=' * len(a_subreddit.display_name)))
        submission = list(a_subreddit.hot(limit=1))[0]
        print("\nTitle:", submission.title)
        print("URL: " + submission.url)
        print("Author:", submission.author)
        print("\n")
        submission.sort = 'top'
        path = "rtemp" + ".mp4"
        prompt_create_submission_video(submission, path)
        uploaded = True
        upload_response = None
        try:
            upload_response = upload_video(path,
                                           description=DESCRIPTION + "Link to subreddit post: " + submission.url + "\n" +
                                                       submission.title, title="AskReddit: " +
                                                                               submission.title,
                                           keywords="AskReddit, Reddit")
        except:
            uploaded = False
        if uploaded:
            uploaded_vids_db.insert(
                {"reddit_url": submission.url, "permanent_reddit_url": submission.permalink,
                 "youtube": upload_response})
        clean_temp()


if __name__ == '__main__':
    main()
