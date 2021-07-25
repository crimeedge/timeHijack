from re import compile
from typing import Pattern

video_id_prog: Pattern[str] = compile(r'v=([^&,]+)')
time_prog: Pattern[str] = compile(r'&t=([^&]+)')
comment_prog: Pattern[str] = compile(r'(\d)+:(\d\d)')
youtube_prog: Pattern[str] = compile(r'youtube\.com')
be_prog: Pattern[str] = compile(r'youtu.be/([^\?,%#]+)')
