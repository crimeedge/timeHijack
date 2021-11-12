# -*- coding: utf-8 -*-
from googleapiclient.errors import HttpError
from selenium.webdriver.support.ui import WebDriverWait
import re
import json
from collections import defaultdict
from driverMethods import create_driver
from progs import video_id_prog, time_prog, comment_grabber_prog, comment_grabber_prog_weak
#from youtube.youtubeComments import get_comment_time, get_time_from_comment
import youtube.youtubeComments as youtubeComments
from youtube.youtubeMake import get_api_service
from multiprocessing import Process, Lock
import testdl

video_id = "INIT"


def check_diff_video_id(driver):
    # global driver
    global video_id
    vee = video_id_prog.search(driver.current_url)
    # print("debug:"+vee)
    if vee:
        if not video_id == vee.group(1):
            return True
    return False


def main():
    lock = Lock()
    youtube = get_api_service()
    # global driver
    driver = create_driver(True, True)
    # login_to_youtube(driver)
    driver.get("https://www.youtube.com/channel/UCuQjQ-iqbHh-hIMrDwfYfYA/")
    global video_id
    for _ in range(99999):
        print(video_id)
        #store previous id
        prev_id = video_id
        WebDriverWait(driver, 99999).until(check_diff_video_id)
        # print(video_id)
        video_id = video_id_prog.search(driver.current_url).group(1)
        # print(video_id)
        id = video_id
        ms_pair = None

        filename = "dIAll.json"
        f = open(filename, 'r')
        cached_dict = defaultdict(lambda: dict(), json.load(f))
        f.close()
        # cache
        if id in cached_dict and "tim" in cached_dict[id] and len(cached_dict[id]["tim"]) > 0:
            ms_pair = youtubeComments.get_time_from_comment(
                cached_dict[id]["tim"][0])

        #notcache
        if not ms_pair:
            try:
                ms_pair = youtubeComments.get_comment_time(youtube, video_id)
                print("nocache", ms_pair)
            except HttpError as err:
                print(err)
                ms_pair = None
        #check prev and update also # modularize??? prev_id and id and timegrabber...

        #safety checks
        if prev_id in cached_dict and "tim" in cached_dict[prev_id] and len(cached_dict[prev_id]["tim"]) > 0:
            try:

                if cached_dict[prev_id]["tim"][1] == "":
                    comment = youtubeComments.get_one_comment(
                        youtube, prev_id, "Undesirable Truism")
                    if comment:
                        for i, line in enumerate(comment.splitlines()):
                            tim = comment_grabber_prog.search(line)
                            #populate the time by the group prog to the line
                            # expand list if necessary
                            if tim:
                                if 2*i+2 > len(cached_dict[prev_id]["tim"]):
                                    cached_dict[prev_id]["tim"].extend(
                                        [""]*(2*i+2-len(cached_dict[prev_id]["tim"])))
                                cached_dict[prev_id]["tim"][2*i] = tim.group(1)
                                cached_dict[prev_id]["tim"][2 *
                                                            i+1] = tim.group(2)
                                print("tim", tim.group(2))
                            else:

                                tim_weak = comment_grabber_prog_weak.search(
                                    line)
                                print("tim_weak", tim_weak)
                                if tim_weak:
                                    if 2*i+2 > len(cached_dict[prev_id]["tim"]):
                                        cached_dict[prev_id]["tim"].extend(
                                            [""]*(2*i+2-len(cached_dict[prev_id]["tim"])))
                                    cached_dict[prev_id]["tim"][2 *
                                                                i] = tim_weak.group(1)
                                    # print("tim_weak",tim_weak.group(1))
                        with open(filename, 'w') as outfile:
                            outfile.write(json.dumps(cached_dict, indent=4))
                # try downloading in processes, should be ALL PREV
                for i in range(0, len(cached_dict[prev_id]["tim"]), 2):
                    ss = cached_dict[prev_id]["tim"][i]
                    to = cached_dict[prev_id]["tim"][i+1]
                    print("startdl", prev_id, ss, to)
                    Process(target=testdl.download_one_cache_wrap,
                            args=(prev_id, ss, to, lock)).start()
                    print("ENDDL", prev_id, ss, to)
            except HttpError as err:
                print(err)
                pass

        #10 sec barrier
        if ms_pair and (int(ms_pair[0]) > 0 or int(ms_pair[1]) > 10):
            hijacked_link = re.sub(
                time_prog, "", driver.current_url) + '&t=' + ms_pair[0] + 'm' + ms_pair[1] + 's'
            print(hijacked_link)
            driver.get(hijacked_link)


if __name__ == "__main__":
    main()
