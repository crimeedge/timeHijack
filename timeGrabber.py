from youtube import youtubeMake
from youtube.youtubePlaylistItems import get_playlist_items_from_id
import youtube.youtubeComments as youtubeComments
import json
from collections import defaultdict
from progs import comment_grabber_prog, comment_grabber_prog_weak
from googleapiclient.errors import HttpError

def get_video_ids_and_pos(items):
    video_ids = dict()
    for item in items:
        position_dict = dict()
        position_dict["cap"] = item['snippet']['title']
        position_dict["pos"] = item['snippet']['position']
        video_ids[item['snippet']['resourceId']['videoId']] = position_dict
    return video_ids

def update_dict_playlists(cached_dict,items,playlistName):
    print("udpate_dict",playlistName)
    for item in items:
        id = item['snippet']['resourceId']['videoId']
        print("udatedict id",id)
        if id in cached_dict:
            print("isid")
            if "nam" not in cached_dict[id]:
                cached_dict[id]["nam"]=dict()
            cached_dict[id]["nam"][playlistName]="" #make dictionary for this in json!




if __name__ == "__main__":
    reset_cache = False
    
    filename = "dIAll.json"
    cached_dict = defaultdict(lambda: dict(), json.load(open(filename, 'r')))
    youtube = youtubeMake.get_api_service()
    playlist_ids = "PLXoAM842ovaA_RSh_qFXCKC4dT780z5P5".split(",") #only IAll
    items = []
    for playlist_id in playlist_ids:
        items.extend(get_playlist_items_from_id(youtube, playlist_id))
    video_ids = get_video_ids_and_pos(items)

    #update position, and one-idx
    for id in video_ids:
        cached_dict[id]["pos"]=video_ids[id]["pos"]+1
        cached_dict[id]["cap"]=video_ids[id]["cap"]
        #hard code some json garbage to setup times
        if "tim" not in cached_dict[id]:
            cached_dict[id]["tim"]=["",""]
            # if nothing in the end time
        if (cached_dict[id]["tim"][1]=="" or reset_cache) and cached_dict[id]["pos"]<=82:
        # if (cached_dict[id]["tim"][1]=="" or reset_cache) and cached_dict[id]["pos"]<=82:
            try:
                comment = youtubeComments.get_one_comment(youtube,id,"Undesirable Truism")
                if comment:
                    for i,line in enumerate(comment.splitlines()):
                        print("line",video_ids[id]["pos"]+1,line)
                        tim = comment_grabber_prog.search(line)
                        #populate the time by the group prog to the line
                        # expand list if necessary
                        if tim:
                            if 2*i+2 > len(cached_dict[id]["tim"]):
                                cached_dict[id]["tim"].extend([""]*(2*i+2-len(cached_dict[id]["tim"])))
                            cached_dict[id]["tim"][2*i]=tim.group(1)
                            cached_dict[id]["tim"][2*i+1]=tim.group(2)
                            print("tim",tim.group(2))
                        else:
                            
                            tim_weak = comment_grabber_prog_weak.search(line)
                            print("tim_weak",tim_weak)
                            if tim_weak:
                                if 2*i+2 > len(cached_dict[id]["tim"]):
                                    cached_dict[id]["tim"].extend([""]*(2*i+2-len(cached_dict[id]["tim"])))
                                cached_dict[id]["tim"][2*i]=tim_weak.group(1)
                                # print("tim_weak",tim_weak.group(1))
            except HttpError as err:
                print(err)
                pass

    playdict = dict()
    with open("playlistMap.json",'r') as f:
        playdict = dict(json.load(f))
    for playlistName in playdict:
        update_dict_playlists(cached_dict,get_playlist_items_from_id(youtube, playdict[playlistName][0]),playlistName) #feed source
             

    with open(filename, 'w') as outfile:
        outfile.write(json.dumps(cached_dict, indent=4))