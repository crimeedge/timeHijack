from re import compile
from typing import Pattern

insta_id_prog: Pattern[str] = compile(r'instagram.com/p/(.+)/')
video_id_prog: Pattern[str] = compile(r'v=([^&,]+)')
time_prog: Pattern[str] = compile(r'&t=([^&]+)')
comment_prog: Pattern[str] = compile(r'(\d+):(\d\d)')
comment_grabber_prog: Pattern[str]=compile(r'((?:\d+:)+\d+)\s+((?:\d+:)+\d+)')
comment_grabber_prog_weak: Pattern[str]=compile(r'((?:\d+:)+\d+)')
youtube_prog: Pattern[str] = compile(r'youtube\.com')
be_prog: Pattern[str] = compile(r'youtu.be/([^\?,%#]+)')
download_prog: Pattern[str]=compile(r'.*\\(.+?)@.*')
upload_prog: Pattern[str]=compile(r'(.+?)@.*')
desc_prog: Pattern[str]=compile(r'([^#]+)#(\d+?)\.(\d+?)#.*')
desc_big_prog: Pattern[str]=compile(r'([^#]+)#(\d+?)\.(\d+?)\.(\d+?)#.*')