from __future__ import unicode_literals

import yt_dlp as youtube_dl
import json
from collections import defaultdict

def download_one_vid(id,ss,to):
    ydl_opts = {      
        'outtmpl': 'videos\\%(title).100s'+ss+'.'+to+'.%(resolution)s.%(id)s.v1.%(ext)s',        
        'noplaylist' : True,    
        'socket_timeout': 60, 
        #'progress_hooks': [my_hook],
        #'compat_opts': 'no-direct-merge',
        #'format': 'bestvideo[vcodec*=avc1][height=1080]+bestaudio[acodec*=aac]/bestvideo[vcodec*=avc1][height=1080]+bestaudio[acodec*=mp3]/bestvideo[vcodec*=avc1][height=1080]+bestaudio[acodec*=mp4a]/bestvideo[height=1080]+bestaudio/bestvideo[vcodec*=avc1][height<=?1080]+bestaudio[acodec*=aac]/bestvideo[vcodec*=avc1][height<=?1080]+bestaudio[acodec*=mp3]/bestvideo[vcodec*=avc1][height<=?1080]+bestaudio[acodec*=mp4a]/bestvideo[vcodec*=avc1][height<=?1080]+bestaudio/bestvideo[height<=?1080]+bestaudio[acodec=aac]/bestvideo[height<=?1080]+bestaudio[acodec=mp3]/bestvideo[height<=?1080]+bestaudio[acodec=mp4a]/bestvideo[height<=?1080]+bestaudio/best',
        'external_downloader': 'ffmpeg' , 
        'external_downloader_args': {
            'ffmpeg_i': ['-ss', ss, '-to', to],
        }
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([id])
        except youtube_dl.utils.DownloadError as err:
            print(err)

def main():
    filename = "dIAll.json"
    cached_dict = defaultdict(lambda: dict(), json.load(open(filename, 'r')))
    for id in (cached_dict):
        if "tim" in cached_dict[id] :
            for i in range(0,len(cached_dict[id]["tim"]),2):
                if cached_dict[id]["tim"][i] != "" and cached_dict[id]["tim"][i+1] != "":
                    download_one_vid(id,cached_dict[id]["tim"][i],cached_dict[id]["tim"][i+1])

if __name__ == "__main__":
    main()

