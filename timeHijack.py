# -*- coding: utf-8 -*-
from googleapiclient.errors import HttpError
from selenium.webdriver.support.ui import WebDriverWait
import re
import json
from collections import defaultdict
from driverMethods import create_driver
from progs import video_id_prog, time_prog
from youtube.youtubeComments import get_comment_time, get_time_from_comment
from youtube.youtubeMake import get_api_service

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
    filename = "dIAll.json"
    f=open(filename, 'r')
    cached_dict = defaultdict(lambda: dict(), json.load(f))
    f.close()
    youtube = get_api_service()
    # global driver
    driver = create_driver(True, True)
    # login_to_youtube(driver)
    driver.get("https://www.youtube.com/channel/UCuQjQ-iqbHh-hIMrDwfYfYA/")
    global video_id

    for _ in range(99999):
        print(video_id)
        WebDriverWait(driver, 99999).until(check_diff_video_id)
        # print(video_id)
        video_id = video_id_prog.search(driver.current_url).group(1)
        # print(video_id)
        id = video_id
        ms_pair = None
        if id in cached_dict and "tim" in cached_dict[id] and len(cached_dict[id]["tim"])>0:
            ms_pair = get_time_from_comment(cached_dict[id]["tim"][0])
            print("cached stuff yea")
        if not ms_pair:
            try:
                ms_pair = get_comment_time(youtube, video_id)
                print(ms_pair)
            except HttpError as err:
                print(err)
                ms_pair = None
        # 10 sec barrier
        if ms_pair and (int(ms_pair[0]) > 0 or int(ms_pair[1]) > 10):
            hijacked_link = re.sub(time_prog, "", driver.current_url) + '&t=' + ms_pair[0] + 'm' + ms_pair[1] + 's'
            print(hijacked_link)
            driver.get(hijacked_link)
    # print(get_comment_time(youtube))


if __name__ == "__main__":
    main()
