#!/usr/bin/env python

import subprocess
import time
from format import *

class Video():
    """ Class to represent a Youtube video."""

    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.user = data['uploader']
        self.uploaded = time.strptime(data['uploaded'].replace(".000Z", "").replace("T", " "), "%Y-%m-%d %H:%M:%S")
        self.views = int(data['viewCount']) if 'viewCount' in data else 0
        self.rating = float(data['rating']) if 'rating' in data else 0
        self.likes = int(data['likeCount']) if 'likeCount' in data else 0
        self.dislikes = int(data['ratingCount']) - self.likes if 'ratingCount' in data else 0
        self.comment_count = int(data['commentCount']) if 'commentCount' in data else 0
        self.length = int(data['duration'])


    def format_title_desc(self, number):
        """Formats information about the title and description of the video."""

        title = str(number) + '. ' + self.title
        desc = self.description
        return (title, desc)


    def format_info(self):
        """Formats other information about the video."""
        

        user = ' ' + quick_fit_string(self.user, 21)
        info1 = ' v:' + format_int(self.views, 4) + \
                ' t:' + quick_fit_string(format_time(self.length), 8)
        info2 = ' l:' + format_int(self.likes, 4) + \
                ' d:' + format_int(self.dislikes, 4) + \
                ' r:' + quick_fit_string(str(self.rating), 4)
        info3 = ' r:' + quick_fit_string(str(self.rating), 4) + \
                ' u:' + time.strftime('%d/%m/%y', self.uploaded)
        return (user, info1, info3)


    def play(self, player, args):
        """Opens the video in a video player"""

        url = 'https://www.youtube.com/watch?v=' + self.id
        player = subprocess.Popen([player] + args.split(' ') +  [url], stderr=subprocess.DEVNULL)

