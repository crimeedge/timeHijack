from __future__ import unicode_literals

import yt_dlp as youtube_dl
import subprocess

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {      
    'outtmpl': '%(title)s.%(resolution)s.%(id)s.vT.%(ext)s',        
    'noplaylist' : True,
    'trim_file_name': 500,        
    #'progress_hooks': [my_hook],
    #'compat_opts': 'no-direct-merge',
    #'format': 'bestvideo[vcodec*=avc1][height=1080]+bestaudio[acodec*=aac]/bestvideo[vcodec*=avc1][height=1080]+bestaudio[acodec*=mp3]/bestvideo[vcodec*=avc1][height=1080]+bestaudio[acodec*=mp4a]/bestvideo[height=1080]+bestaudio/bestvideo[vcodec*=avc1][height<=?1080]+bestaudio[acodec*=aac]/bestvideo[vcodec*=avc1][height<=?1080]+bestaudio[acodec*=mp3]/bestvideo[vcodec*=avc1][height<=?1080]+bestaudio[acodec*=mp4a]/bestvideo[vcodec*=avc1][height<=?1080]+bestaudio/bestvideo[height<=?1080]+bestaudio[acodec=aac]/bestvideo[height<=?1080]+bestaudio[acodec=mp3]/bestvideo[height<=?1080]+bestaudio[acodec=mp4a]/bestvideo[height<=?1080]+bestaudio/best',
    'external_downloader': 'ffmpeg' , 
    'external_downloader_args': {
        'ffmpeg_i': ['-ss', '13:58', '-to', '15:20'],
        'c':['v','ffv1']
    }
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['8-VWeTQaxjE'])


   