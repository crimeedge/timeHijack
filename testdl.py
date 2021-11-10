from __future__ import unicode_literals

import yt_dlp as youtube_dl
import json
from collections import defaultdict
import ffmpeg
import subprocess

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

def my_hook(d):
    if d['status']=='finished':
        print("HIIII!!!!",d['filename'])
        trim(d['filename'])

def download_one_vid(id,ss,to):
    ydl_opts = {      
        'outtmpl': 'videos\\%(title).100s'+ss+'.'+to+'.%(resolution)s.%(id)s.v1.%(ext)s',        
        'noplaylist' : True,    
        'download_archive': 'archive.txt',
        'external_downloader': 'ffmpeg' , 
        'sleep_interval': 3,
        'max_sleep_interval': 5,
        'external_downloader_args': {
            'ffmpeg_i': ['-ss', ss, '-to', to],
        },
        'progress_hooks':[my_hook]
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
        # if "tim" in cached_dict[id] and cached_dict[id]['pos']>=21:
        if "tim" in cached_dict[id] and cached_dict[id]['pos']<=5:
            for i in range(0,len(cached_dict[id]["tim"]),2):
                if cached_dict[id]["tim"][i] != "" and cached_dict[id]["tim"][i+1] != "":
                    download_one_vid(id,cached_dict[id]["tim"][i],cached_dict[id]["tim"][i+1])

if __name__ == "__main__":
    main()

