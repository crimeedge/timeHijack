from progs import comment_prog

def get_comment_time(youtube, video_id, comment_author="Undesirable Truism"):
    request = youtube.commentThreads().list(
        part="snippet",
        searchTerms=comment_author,
        videoId=video_id
    )
    response = request.execute()
    for item in response['items']:
        if item['snippet']['topLevelComment']['snippet']['authorDisplayName'] == comment_author:
            comment = item['snippet']['topLevelComment']['snippet']['textOriginal']
            min_sec = comment_prog.search(comment)
            if min_sec:
                return min_sec.group(1), min_sec.group(2)

    return None
