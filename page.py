import curses
from query import *

class Page():
    """A class respenting a page in the UI."""


    def __init__(self, type):
        """Creates a new Page object with default values."""

        self.type = type
        self.videos = []
        self.start = 0


    def format(self):
        """Returns a short string containing information about the page."""

        if (self.type == 'bookmarks' or self.type == 'subscriptions'):
            return self.type
        elif (not hasattr(self, 'user')):
            return 'new search'
        elif (self.user == ''):
            return 's:' + self.term
        else:
            return 'u:' + self.user + '/' + self.term


    def draw_main_pane(self, win, ui):
        """Redraws the main pane."""

        h, w = win.getmaxyx()
        h -= 2
        info_pane_start = w - ui.info_width if not ui.simple_video_format else w
        info_pane = curses.newwin(h, ui.info_width, 0, info_pane_start)
        item_height = 2 if ui.simple_video_format else 3
        main_pane = curses.newwin(h + item_height - 1, info_pane_start, 0, 0)
        videos_per_page = h // item_height
        start = self.start
        end = min(len(self.videos), start + videos_per_page)
        start = max(min(start, end - videos_per_page), 0)
        self.start = start
        self.end = end
        y = 0
        for video in self.videos[start:end]:
            if (ui.show_real_index):
                title, desc = video.format_title_desc(y // item_height + start + 1)
            else:
                title, desc = video.format_title_desc(y // item_height)
            if (ui.simple_video_format):
                main_pane.addstr(y, 0, title, ui.title_style)
                user = video.user
                main_pane.addstr(y, w - len(user), user, ui.title_style)
                info = [ 'views:' + format_int(video.views, 4)\
                       , 'duration:' + quick_fit_string(format_time(video.length), 8)\
                       , 'rating:' + quick_fit_string(str(video.rating), 4)\
                       , 'likes:' + format_int(video.likes, 4)\
                       , 'dislikes:' + format_int(video.dislikes, 4)\
                       , 'date:' + time.strftime('%d/%m/%y', video.uploaded)]
                main_pane.addstr(y + 1, 0, center(info, w))
                y += 2
            else:
                user, info1, info2 = video.format_info()
                main_pane.addstr(y, 0, title, ui.title_style)
                info_pane.addstr(y, 0, user, ui.title_style)
                y += 1
                main_pane.addstr(y, 0, desc)
                info_pane.addstr(y, 0, info1)
                y += 1
                info_pane.addstr(y, 0, info2)
                y += 1
        main_pane.refresh()
        info_pane.refresh()


class BookmarkPage(Page):
    """Class representing a page of bookmarks."""
    
    def swap(self, video, shift):
        """Swaps 2 items in a list."""
    
        index = self.videos.index(video)
        if ((index == 0 and shift < 0) or (index == len(self.videos) - 1 and shift > 0)):
            return
        else:
            self.videos[index + shift], self.videos[index] = self.videos[index], self.videos[index + shift]
     
    def delete(self, video):
        """Deletes an item in a list."""

        index = self.videos.index(video)
        self.videos = self.videos[:index] + self.videos[index + 1:]
    

    def add_bookmark(self, video):
        """Adds a bookmark to a bookmark page."""

        self.videos.append(video)


class SearchPage(Page):
    """Class representing a page of search results."""

    def add_search(self, user, term, ordering, max_results):
        """Performs a search on a search page."""

        self.user = user
        self.term = term
        self.ordering = ordering
        self.max_results = max_results
        if (user != ''):
            self.videos = search_user(user, term, ordering, max_results)
        else:
            self.videos = search_term(term, ordering, max_results)


class SubscriptionPage(Page):
    """Class representing a list of subscriptiosn."""

    def add_user(self, user):
        """Adds a user to a subscription page."""

        assert self.type == 'subscriptions', 'cannot add a user to a non-suscription page'
        if (not hasattr(self, 'user_list')):
            self.user_list = []
        self.user_list.append(user)

    
    def refresh_subs(self, max_results):
        """Refreshes the subscription list."""

        assert self.type == 'subscriptions', 'cannot refresh a non-suscription page'
        if (hasattr(self, 'user_list')):
            self.videos = []
            for user in self.user_list:
                self.videos.extend(search_user(user, '', 'published', max_results))
            self.videos.sort(key = lambda video: video.uploaded)
            self.videos.reverse()


