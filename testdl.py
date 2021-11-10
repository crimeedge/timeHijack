from __future__ import unicode_literals

import yt_dlp as youtube_dl
import json
from collections import defaultdict
import ffprobe

def download_one_vid(id,ss,to):
    ydl_opts = {      
        'outtmpl': 'videos\\%(title).100s'+ss+'.'+to+'.%(resolution)s.%(id)s.v1.%(ext)s',        
        'noplaylist' : True,    
        'download_archive': 'archive.txt',
        'external_downloader': 'ffmpeg' , 
        'sleep_interval': '3',
        'max_sleep_interval': '5',
        'external_downloader_args': {
            'ffmpeg_i': ['-ss', ss, '-to', to],
        }
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([id])
        except youtube_dl.utils.DownloadError as err:
            print('ERRROR!!!!!!')
            print(err)

def main():
    filename = "dIAll.json"
    cached_dict = defaultdict(lambda: dict(), json.load(open(filename, 'r')))
    for id in (cached_dict):
        if "tim" in cached_dict[id] and cached_dict[id]['pos']>=21:
            for i in range(0,len(cached_dict[id]["tim"]),2):
                if cached_dict[id]["tim"][i] != "" and cached_dict[id]["tim"][i+1] != "":
                    download_one_vid(id,cached_dict[id]["tim"][i],cached_dict[id]["tim"][i+1])

if __name__ == "__main__":
    main()

