import string
import random
import textwrap
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np
from moviepy.editor import *
import soundfile as sf
from pydub import AudioSegment
from pydub.playback import play

from gtts import gTTS
from io import BytesIO

from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_left_right import audio_left_right
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex

from pathlib import Path

WIDTH = 1920
HEIGHT = 1080
BACKGROUND_TRACK = "assets/tetris_loop.wav"
TRANSITION_CLIP = "assets/static_transition.mov"
INTRO_CLIP = "assets/logo_appear.mov"
HARD_LINE_BREAK_AFTER = 90


def gen_comment_image(author, content):
    content = process_content(content)
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(26, 26, 27))
    fnt = ImageFont.truetype('sans-serif.ttf', 45)
    d = ImageDraw.Draw(img)
    d.text((10, 10), author, fill=(79, 188, 255), font=fnt)
    d.multiline_text((10, 60), content, fill=(
        255, 255, 255), font=fnt, align="left")
    return np.array(img)


def process_content(text):
    # need to add removal of profain words.
    return add_newlines(text)


def add_newlines(text):
    res: str = ""
    curr = 0
    last_space_pos = 0
    for index, char in enumerate(text):
        last_space_pos = index if char == ' ' else last_space_pos
        if curr < HARD_LINE_BREAK_AFTER:
            curr = curr + 1
        else:
            curr = 0
            # res = res + "-\n"
            res = change_char(res, last_space_pos, '\n')
        res = res + char
    return res


def change_char(s, p, r):
    return s[:p]+r+s[p+1:]


def gen_title_message_image(msg):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(26, 26, 27))
    fnt = ImageFont.truetype('sans-serif.ttf', 60)
    d = ImageDraw.Draw(img)
    d.text((10, 10), msg, fill=(200, 188, 255), font=fnt)
    return np.array(img)


def gen_title_message_clip(msg):
    background_clip = ImageClip(gen_title_message_image(msg))
    audio_clip = gen_audio_clip(msg)
    background_clip = background_clip.set_duration(audio_clip.duration)
    background_clip = background_clip.set_audio(audio_clip)
    return background_clip


def create_comment_clip(author, content):
    background_clip = ImageClip(
        gen_comment_image(author=author, content=content))
    audio_clip = gen_audio_clip(content)
    # audio_clip.preview()
    # duration is determined by the audio clip duration
    background_clip = background_clip.set_duration(audio_clip.duration)
    background_clip = background_clip.set_audio(audio_clip)
    # background_clip.preview()
    return background_clip


def randomStringDigits(stringLength=6):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


def gen_audio_clip(text):
    tts = gTTS(text, 'en')
    name = "rtemp" + randomStringDigits(8) + ".mp3"
    tts.save(name)
    clip = AudioFileClip(name)
    # delete the rtemp file
    clean_temp()
    return clip


def audio_concatenate(clips):
    durations = [c.duration for c in clips]
    tt = np.cumsum([0]+durations)  # start times, and end time.
    newclips = [c.set_start(t) for c, t in zip(clips, tt)]
    return CompositeAudioClip(newclips).set_duration(tt[-1])


def audio_loop_(clip, duration):
    nloops = int(duration / clip.duration)+1
    return audio_concatenate(nloops*[clip]).set_duration(duration)


def gen_background_audio_clip(length: int):
    return audio_loop_(AudioFileClip(BACKGROUND_TRACK), length)


def gen_transition_clip():
    clip = VideoFileClip(TRANSITION_CLIP)
    clip.audio = clip.audio.fx(volumex, 0.3)
    return clip


def gen_intro_clip():
    return VideoFileClip(INTRO_CLIP)


def clean_temp():
    for p in Path(".").glob("rtemp*"):
        p.unlink()
