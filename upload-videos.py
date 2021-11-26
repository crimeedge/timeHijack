

import re
import httplib2
import os
import random
import time
from googleapiclient.errors import HttpError
from youtube.youtubeMake import get_authenticated_service
import os

import youtube.youtubePlaylistItems as ytpi

from collections import defaultdict
import json
from types import SimpleNamespace
from progs import upload_prog, desc_prog, desc_big_prog

from googleapiclient.http import MediaFileUpload

from oauth2client.tools import argparser, run_flow


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 1

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError
                        # ,
                        #  httplib.NotConnected,
                        #   httplib.IncompleteRead, httplib.ImproperConnectionState,
                        #   httplib.CannotSendRequest, httplib.CannotSendHeader,
                        #   httplib.ResponseNotReady, httplib.BadStatusLine
                        )

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body = dict(
      snippet=dict(
          title=options.title,
          description=options.description,
          tags=tags,
          categoryId=options.category
      ),
      status=dict(
          privacyStatus=options.privacyStatus
      )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
      part=",".join(body.keys()),
      body=body,
      # The chunksize parameter specifies the size of each chunk of data, in
      # bytes, that will be uploaded at a time. Set a higher value for
      # reliable connections as fewer chunks lead to faster uploads. Set a lower
      # value for better recovery on less reliable connections.
      #
      # Setting "chunksize" equal to -1 in the code below means that the entire
      # file will be uploaded in a single HTTP request. (If the upload fails,
      # it will still be retried where it left off.) This is usually a best
      # practice, but if you're using Python older than 2.6 or if you're
      # running on App Engine, you should set the chunksize to something like
      # 1024 * 1024 (1 megabyte).
      media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  return resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.


def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print("Video id '%s' was successfully uploaded." % response['id'])
          return response
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print(error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)
    return None

# gonna need to modularlize this too

def update_video(youtube,id,options):
    try:
        request = youtube.videos().update(
            part="snippet,status",
            body={
            "id": id,
            "snippet": {
                "description": options.description,
                "title": options.title,
                "categoryId": options.category
            },
            "status": {
                "privacyStatus":options.privacyStatus
            }
            }
        )
        return request.execute()
    except BaseException as e:
        print(e)
        return None


def insert_vid_into_playlist(youtube, video_id, playlist_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    response = request.execute()
    return response

def get_video_ids_and_pos(items):
    video_ids = dict()
    for item in items:
        position_dict = dict()
        position_dict["cap"] = item['snippet']['title']
        position_dict["pos"] = item['snippet']['position']
        video_ids[item['snippet']['resourceId']['videoId']] = position_dict
    return video_ids


def make_opts(dir, title_or_filename):
    db = desc_big_prog.match(title_or_filename)
    dd = desc_prog.match(title_or_filename)
    opts = None 
    description = ""
    if db:
        description = r'https://www.youtube.com/watch?v=' + \
                        db.group(1)+r'&list=PLXoAM842ovaA_RSh_qFXCKC4dT780z5P5' + \
                        '&t=' + db.group(2) + 'h' + \
                        db.group(3) + 'm'+db.group(4) + 's' + '\n' + r'https://www.youtube.com/watch?v=' + \
                        db.group(1) + \
                        '&t=' + db.group(2) + 'h' + \
                        db.group(3) + 'm'+db.group(4) + 's'
        opts = SimpleNamespace(
                        privacyStatus="unlisted", title=title_or_filename, description=description, file=dir+"\\"+title_or_filename, category="22", keywords="",oldid=db.group(1))
        
    elif dd:
        description = r'https://www.youtube.com/watch?v=' + \
                        dd.group(1)+r'&list=PLXoAM842ovaA_RSh_qFXCKC4dT780z5P5' + \
                        '&t=' + dd.group(2) + 'm'+dd.group(3) + 's' + '\n' + r'https://www.youtube.com/watch?v=' + \
                        dd.group(1) + \
                        '&t=' + dd.group(2) + 'm'+dd.group(3) + 's'
        opts = SimpleNamespace(
                        privacyStatus="unlisted", title=title_or_filename, description=description, file=dir+"\\"+title_or_filename, category="22", keywords="",oldid=dd.group(1))
             
    return opts

# try to playlist up the already uploaded lists.
def re_playlist(youtube, downloaded):
    vids_dict = get_video_ids_and_pos(
        ytpi.get_playlist_items_from_id(youtube, "UUuQjQ-iqbHh-hIMrDwfYfYA"))
    
    for id in vids_dict:
        title_sig = vids_dict[id]["cap"].split("@")[0] #get the prefix
        print(title_sig,vids_dict[id]["cap"])
        if downloaded[title_sig][2]!=1:
            # check that desc is updated
            # also insert to playlist
            opts = make_opts("",vids_dict[id]["cap"])
            print(str(opts))
            response = update_video(youtube, id, opts)
            print(str(response))
            if opts and response:
                insert_vid_into_playlist(youtube,id,"PLXoAM842ovaC2m60u5BSAHmwjGTpqXGk4")
                downloaded[title_sig][2]=1
                with open("downloadTracker.json", 'w') as outfile:
                    outfile.write(json.dumps(downloaded, indent=4))


def upload_once(UPLOADSMAX = 5,secret="p"):
    youtube = get_authenticated_service(secret=secret)

    cached_dict = dict()
    filename = "dIAll.json"
    with open(filename, 'r') as f:
        cached_dict = defaultdict(lambda: dict(), json.load(f))

    downloaded = defaultdict(lambda: [0]*3)
    with open("downloadTracker.json", 'r') as infile:
      downloaded = defaultdict(lambda: [0]*3, json.load(infile))
    
        
    # re_playlist( youtube, downloaded)


    dir = r'clean\videos'
    
    uploads = 0

    list_of_files = filter( lambda x: os.path.isfile(os.path.join(dir, x)),
                        os.listdir(dir) )
    # Sort list of files based on last modification time in ascending order
    list_of_files = sorted( list_of_files,
                        key = lambda x: os.path.getmtime(os.path.join(dir, x))
                        )


    for filename in list_of_files:
        if uploads >= UPLOADSMAX:
            break
        match_obj = upload_prog.match(filename)
        if match_obj:
            downloaded = dict()  # important to not b default
            with open("downloadTracker.json", 'r') as infile:
                downloaded = dict(json.load(infile))
            if match_obj.group(1) in downloaded and len(downloaded[match_obj.group(1)]) >= 3 and downloaded[match_obj.group(1)][2] != 1:
                print(filename)
                opts = make_opts(dir, filename)
                if opts:
                    try:
                        response = initialize_upload(youtube, opts)
                        if response:
                            print("uploaded",opts.title)
                            downloaded = defaultdict(lambda: [0]*3)
                            with open("downloadTracker.json", 'r') as infile:
                                downloaded = defaultdict(
                                    lambda: [0]*3, json.load(infile))
                            downloaded[match_obj.group(1)][2] = 1
                            uploads += 1 

                            playdict = dict()
                            with open("playlistMap.json",'r') as f:
                                playdict = dict(json.load(f))

                            new_id = response["id"]
                            for nam in cached_dict[opts.oldid]["nam"]:
                                resp2=insert_vid_into_playlist(youtube,new_id,playdict[nam][1]) #mappedto
                                print(new_id,resp2['kind'])

                            with open("downloadTracker.json", 'w') as outfile:
                                outfile.write(json.dumps(downloaded, indent=4))
                    except HttpError as e:
                        print("An HTTP error %d occurred:\n%s" %
                                (e.resp.status, e.content))

if __name__ == '__main__':
    for secret in ["p","o","q"]: #rstu TaP policy locked
        upload_once(5,secret)
