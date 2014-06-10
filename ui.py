#!/usr/bin/env python3

import curses
import math
import os
import pickle
from format import *
from page import *
from query import *
from video import *

class Ui():
    """The main Ui."""

    def __init__(self):
        self.max_results = 20
        self.info_width = 21
        self.title_color = curses.COLOR_GREEN
        self.bold_title = True
        self.current_page_color = curses.COLOR_GREEN
        self.bold_current_page = True
        self.user_order = 'published'
        self.search_order = 'relevance'
        self.open_searches_in_new_page = True
        self.player = 'mpv'
        self.player_args = '--no-terminal'
        self.pages = []
        self.next_message = ''
        self.pages.append(Page('subscriptions'))
        self.pages.append(Page('bookmarks'))
        if (not self.open_searches_in_new_page):
            self.pages.append(Page('search result'))
            self.page_index = 2
        else:
            self.page_index = 1


    def run_ui(self):
        """Sets up the ncurses interface."""

        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, self.title_color, -1)
        curses.init_pair(2, self.current_page_color, -1)
        self.title_style = curses.color_pair(1)
        if (self.bold_title):
            self.title_style = self.title_style ^ curses.A_BOLD
        self.current_page_style = curses.color_pair(2)
        if (self.bold_current_page):
                self.current_page_style = self.current_page_style ^ curses.A_BOLD
        self.draw_screen()
        self.loop()


    def draw_screen(self):
        """Redraws the entire screen."""

        h, w = self.screen.getmaxyx()
        info_pane_start = w - self.info_width
        self.main_pane = curses.newwin(h-2, info_pane_start, 0, 0)
        self.info_pane = curses.newwin(h-2, self.info_width, 0, info_pane_start)
        self.page_bar = curses.newwin(1, w + 2, h - 2, 0)
        self.status_bar = curses.newwin(1, w + 2, h - 1, 0)
        self.draw_main_pane()
        self.draw_page_bar()
        self.draw_status_bar()
        

    def draw_status_bar(self):
        """Redraws the status bar."""
        
        if (self.next_message == ''):
            h, w = self.main_pane.getmaxyx()
            videos_per_page = h // 3
            page = self.pages[self.page_index]
            start = page.start
            end = min(len(page.videos) - 1, start + videos_per_page)
            status = 'displaying videos ' + str(start) + '-' + str(end) + ' of '
            if (page.type == 'search result'):
                if (not page.videos and not hasattr(page, 'user')):
                    status = 'new page'
                elif (not page.videos):
                    status = 'no results found for ' + (page.term if page.user == '' else page.user + '/' + page.term)
                elif (page.user == ''):
                    status += 'results for "' + page.term + '" ordered by ' + page.ordering
                else:
                    status += 'uploads by ' + page.user + ' ordered by ' + page.ordering
            else:
                status += page.type
                if (not page.videos):
                    status = 'no results'
        else:
            status = self.next_message
            self.next_message = ''
        self.status_bar.addstr(0, 0, status)
        self.status_bar.refresh()

    
    def draw_main_pane(self):
        """Redraws the main pane."""

        pane = self.main_pane
        info_pane = self.info_pane
        page = self.pages[self.page_index]
        start = page.start
        h, w = pane.getmaxyx()
        videos_per_page = h // 3
        end = min(len(page.videos), start + videos_per_page)
        y = 0
        for video in page.videos[start:end]:
            title, desc = video.format_title_desc(y // 3)
            user, info1, info2 = video.format_info()
            pane.addstr(y, 0, title, self.title_style)
            info_pane.addstr(y, 0, user, self.title_style)
            y += 1
            pane.addstr(y, 0, desc)
            info_pane.addstr(y, 0, info1)
            y += 1
            info_pane.addstr(y, 0, info2)
            y += 1
        pane.refresh()
        info_pane.refresh()


    def draw_page_bar(self):
        """Redraws the page bar."""

        pages = self.pages
        current = self.page_index
        panel = self.page_bar
        h, w = panel.getmaxyx()
        left = '--'
        right = '--'
        current_page = pages[current].format()
        i = 1
        while (len(left + right + current_page) < w and (current - i >= 0 or current + i < len(pages))):
            prevleft = left
            prevright = right
            left = '--' + pages[current - i].format() + '--' + left if current    - i >= 0 else left
            right = right + '--' + pages[current + i].format() + '--' if current    + i < len(pages) else right
            i += 1
        real_width = get_real_width(left + right + current_page)
        if (real_width > w - 3):
            left, right = prevleft, prevright
            real_width = get_real_width(left + right + current_page)
        while (real_width < w - 3):
            left = '-' + left
            right = right + '-'
            real_width += 2
        if (real_width < w - 1):
            right += '-'
        panel.addstr(0, 0, left)
        panel.addstr(current_page, self.current_page_style)
        panel.addstr(right)
        panel.refresh()


    def get_input(self, prompt):
        """Gets input for a search."""

        curses.echo()
        self.status_bar.erase()
        self.status_bar.addstr(0, 0, prompt)
        curses.curs_set(1)
        self.status_bar.refresh()
        s = self.status_bar.getstr(0, len(prompt)).decode('utf-8')
        curses.noecho()
        curses.curs_set(0)
        return s

    
    def open_new_page(self):
        """Opens a new page after the current page and goes to it."""

        pages = self.pages
        index = self.page_index
        if (index < 1):
            index = 1
        new_page = Page('search result')
        self.pages = pages[0:index + 1] + [new_page] + pages[index + 1:]
        self.page_index += 1


    def loop(self):
        """The main loop of the UI. So much spaghetti code. I will try to fix this eventually"""
    
        while True:
            pages = self.pages
            index = self.page_index
            page = pages[index]
            h, w = self.main_pane.getmaxyx()
            videos_per_page = h // 3
            c = self.status_bar.getch()
            if (c == ord('q')):
                break
            elif (c == ord('j')):
                new_start = page.start + videos_per_page
                if (new_start < len(page.videos)):
                    page.start = new_start
            elif (c == ord('k')):
                new_start = page.start - videos_per_page
                if (new_start > 0):
                    page.start = new_start
                else:
                    page.start = 0
            elif (c == ord('w')):
                if (index > 1):
                    self.pages = pages[0:index] + pages[index + 1:]
                    if (self.page_index >= len(self.pages)):
                            self.page_index -= 1
            elif (c == ord('n')):
                self.open_new_page()
            elif (c == ord('h')):
                self.page_index = max(0, self.page_index - 1)
            elif (c == ord('l')):
                self.page_index = min(len(pages) - 1, self.page_index + 1)
            elif (c == ord('r')):
                if (page.type == 'subscriptions'):
                    page.refresh_subs(self.max_results)
            elif (c == ord('/') or c == ord('.') or c == ord(' ')):
                if (index < 2 and not (self.open_searches_in_new_page and index > 0)):
                    continue
                if (self.open_searches_in_new_page):
                    self.open_new_page()
                    self.draw_screen()
                s = self.get_input("search: ")
                self.pages[self.page_index].add_search('', s, self.search_order, self.max_results)
            elif (c == ord('u')):
                if (index < 2 and not (self.open_searches_in_new_page and index > 0)):
                    continue
                if (self.open_searches_in_new_page):
                    self.open_new_page()
                    self.draw_screen()
                s = self.get_input("search user: ")
                user, term = (s.split('/')[0], s.split('/')[1]) if '/' in s else (s, '')
                self.pages[self.page_index].add_search(user, term, self.user_order, self.max_results)
            elif (c == ord('s')):
                if (index == 0):
                    s = self.get_input("add user: ")
                    videos = search_user(s, '', self.user_order, self.max_results)
                    if (videos):
                        page.add_user(s)
                        self.next_message = 'user ' + s + ' added to subscriptions'
                    else:
                        self.next_message = 'no results found for user ' + s
                elif (index == 1):
                    continue
                else:
                    if (not hasattr(page, 'user') or page.user == ''):
                        self.next_message = 'cannot add to subscriptions: not a user search page'
                    else:
                        s = page.user
                        if (page.videos):
                            self.pages[0].add_user(s)
                            self.next_message = 'user ' + s + ' added to subscriptions'
                        else:
                            self.next_message = 'no results found for user ' + s
            elif (c >= ord('0') and c <= ord('9')):
                video_index = page.start + c - ord('0')
                if (video_index >= len(page.videos)):
                    self.next_message = 'selection index out of range'
                    continue
                n = self.status_bar.getch()
                video = page.videos[video_index]
                if (n == ord('p') or n == 13):
                    self.status_bar.clear()
                    self.status_bar.addstr(0, 0, 'playing: ' + video.title)
                    self.status_bar.refresh()
                    video.play(self.player, self.player_args)
                elif (n == ord('b')):
                    self.pages[1].add_bookmark(video)
                    self.next_message = '"' + video.title + '" added to bookmarks'
                elif (page.type == 'bookmarks'):
                    if (n == ord('k')):
                        page.swap(video, -1)
                    elif (n == ord('j')):
                        page.swap(video, 1)
                    elif (n == ord('d')):
                        page.delete(video) 
            self.draw_screen()


if (__name__ == '__main__'):
    try:
        ui = Ui()
        if (os.path.isfile('session')):
            ui.pages, ui.page_index = pickle.load(open('session', 'rb'))
        else:
            open('session', 'a').close()
        ui.run_ui()
        pickle.dump((ui.pages, ui.page_index), open('session', 'wb'))
    finally:
        curses.endwin()
