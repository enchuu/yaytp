import json
import urllib.request
import urllib.parse
from video import *

def make_query(term, order, max_results):
    """ Makes the query for the search."""
    query = {
        'q': term,
        'v': 2,
        'alt': 'jsonc',
        'start-index': 1,
        'safeSearch': "none",
        'max-results': max_results, 
        'paid-content': "false",
        'orderby': order, 
    }
    return query;


def search(urlbase, term, order, max_results):
    """Helper function for performing a search."""

    query = make_query(term, order, max_results)
    url = urlbase + "?" + urllib.parse.urlencode(query)
    result = urllib.request.urlopen(url).read().decode("utf8")
    try:
        items = json.loads(result)['data']['items']
        videos = []
        for video in items:
            videos.append(Video(video))
    except KeyError:
        videos = []
    return videos


def search_user(user, term, order, max_results):
    """Performs a search on a user's uploads."""

    urlbase = 'https://gdata.youtube.com/feeds/api/users/%s/uploads' % user
    return search(urlbase, term, order, max_results);


def search_term(term, order, max_results):
    """Performs a search on a term."""

    urlbase = 'https://gdata.youtube.com/feeds/api/videos'
    return search(urlbase, term, order, max_results);

