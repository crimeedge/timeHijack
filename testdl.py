from __future__ import unicode_literals
import re

import yt_dlp as youtube_dl
import json
from collections import defaultdict
import ffmpeg
import subprocess
import os

import traceback
from progs import download_prog



from yt_dlp.utils import srt_subtitles_timecode

def probe(filename, cmd='ffprobe', timeout=None, **kwargs):
    """Run ffprobe on the specified file and return a JSON representation of the output.
    Raises:
        :class:`ffmpeg.Error`: if ffprobe returns a non-zero exit code,
            an :class:`Error` is returned with a generic error message.
            The stderr output can be retrieved by accessing the
            ``stderr`` property of the exception.
    """
    args = [cmd, '-read_intervals','%+#1','-show_frames', '-select_streams','v', '-of', 'json']
 
    args += [filename]

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    communicate_kwargs = {}
    if timeout is not None:
        communicate_kwargs['timeout'] = timeout
    out, err = p.communicate(**communicate_kwargs)
    if p.returncode != 0:
        pass
    return json.loads(out.decode('utf-8'))

# trim the file to the first frame
def trim(filename):
    sss = probe(filename)["frames"][0]["best_effort_timestamp_time"]
    print(sss)
    (
        ffmpeg
        .input(filename,ss=sss,analyzeduration="100M",probesize="100M")
        .output('clean\\'+filename,c="copy").overwrite_output().run()
    )
    os.remove(filename)

    #pleasee modularize
    match_obj=download_prog.match(filename)
    if match_obj:
        downloaded = defaultdict(lambda: [0]*3)
        with open("downloadTracker.json", 'r') as infile:
            downloaded = defaultdict(lambda: [0]*3, json.load(infile))
        downloaded[match_obj.group(1)][1]=1
        with open("downloadTracker.json", 'w') as outfile:
            outfile.write(json.dumps(downloaded, indent=4))
def my_hook(d):
    if d['status']=='finished':
        #print("HIIII!!!!",d['filename'])
        match_obj=download_prog.match(d['filename'])
        if match_obj:
            downloaded = defaultdict(lambda: [0]*3)
            with open("downloadTracker.json", 'r') as infile:
                downloaded = defaultdict(lambda: [0]*3, json.load(infile))
            downloaded[match_obj.group(1)][0]=1
            with open("downloadTracker.json", 'w') as outfile:
                outfile.write(json.dumps(downloaded, indent=4))
        
        downloaded = defaultdict(lambda: [0]*3)
        with open("downloadTracker.json", 'r') as infile:
            downloaded = defaultdict(lambda: [0]*3, json.load(infile))
        if not match_obj or downloaded[match_obj.group(1)][1]!=1:
            trim(d['filename'])

def download_one_vid(id,ss,to):
    ydl_opts = {      
        'outtmpl': 'videos\\%(id)s#'+ss.replace(":",".")+'#'+to.replace(":",".")+'@.%(title).50s.%(resolution)s.v1.%(ext)s',        
        'noplaylist' : True,    
        'external_downloader': 'ffmpeg' , 
        'sleep_interval': 1,
        'max_sleep_interval': 2,
        'external_downloader_args': {
            'ffmpeg_i': ['-ss', ss, '-to', to],
        },
        'progress_hooks':[my_hook]
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([id])
        except youtube_dl.utils.DownloadError as err:
            #print('ERRROR!!!!!!')
            traceback.print_exc()

def main():
    filename = "dIAll.json"
    f = open(filename, 'r')
    cached_dict = defaultdict(lambda: dict(), json.load(f))
    f.close()
    for id in (cached_dict):
        if "tim" in cached_dict[id] and cached_dict[id]['pos']<=49:
        # if "tim" in cached_dict[id] and cached_dict[id]['pos']:
            for i in range(0,len(cached_dict[id]["tim"]),2):
                ss=cached_dict[id]["tim"][i]
                to=cached_dict[id]["tim"][i+1]
                download_one_cache_wrap(id, ss, to, None)

def download_one_cache_wrap(id, ss, to, lock):
    if lock:
        lock.acquire()
    try:
        if ss != "" and to != "":
            downloaded = defaultdict(lambda: [0]*3)
            with open("downloadTracker.json", 'r') as infile:
                downloaded = defaultdict(lambda: [0]*3, json.load(infile))
            if downloaded[id+"#"+ss.replace(":",".")+"#"+to.replace(":",".")][0]!=1:
                print("actualdl",id,ss,to)
                download_one_vid(id,ss,to)
    finally:
        if lock:
            lock.release()

if __name__ == "__main__":
    main()

