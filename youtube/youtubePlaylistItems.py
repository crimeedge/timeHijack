import dateutil.parser
import dateutil.tz


def get_playlist_items_from_id(youtube, playlist_id="PLXoAM842ovaC5y2JmwjqNf9M4cosmGO12"):
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=50,
        playlistId=playlist_id
    )
    items = []
    while request:
        response = request.execute()
        items += response["items"]
        request = youtube.playlistItems().list_next(request, response)

    return items


def _parse_date(string):
    dt = dateutil.parser.parse(string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dateutil.tz.UTC)
    return dt

def _req_next(youtube, playlist_id, pageToken):
    return youtube.playlistItems().list(
        part="snippet",
        maxResults=50,
        playlistId=playlist_id,
        pageToken=pageToken
    )

def get_playlist_items_from_liked_id(youtube, playlist_id="LLzjiyMpyPuHnQyVFp9Nimbg",after_date="2019-05-01"):
    """

    :param part:
    :param youtube:
    :param playlist_id:
    :param after_date: a date after which we should stop searching, say "2019-05-01"
    :return:
    """
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=50,
        playlistId=playlist_id
    )
    items = []
    while request:
        response = request.execute()
        items += response["items"]
        if after_date:
            if _parse_date(response["items"][-1]["snippet"]["publishedAt"]) < _parse_date(after_date):
                request = None
            else:
                request = youtube.playlistItems().list_next(request, response)
        else:
            request = youtube.playlistItems().list_next(request, response)

    return items

