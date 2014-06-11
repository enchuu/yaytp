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
        self.save_session = True
        self.max_results = 20
        self.info_width = 21
        self.title_color = curses.COLOR_GREEN
        self.bold_title = True
        self.current_page_color = curses.COLOR_GREEN
        self.bold_current_page = True
        self.user_order = 'published'
        self.search_order = 'relevance'
        self.open_searches_in_new_page = True
        self.show_real_index = True
        self.simple_video_format = True
        self.player = 'mpv'
        self.player_args = '--no-terminal --volume=20'
        self.pages = []
        self.next_message = ''
        self.pages.append(SubscriptionPage('subscriptions'))
        self.pages.append(BookmarkPage('bookmarks'))
        if (not self.open_searches_in_new_page):
            self.pages.append(SearchPage('search result'))
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
        self.page_bar = curses.newwin(1, w + 2, h - 2, 0)
        self.status_bar = curses.newwin(2, w + 2, h - 1, 0)
        self.draw_main_window()
        self.draw_page_bar()
        self.draw_status_bar()
        

    def draw_main_window(self):
        """Redraws the main window."""
        self.pages[self.page_index].draw_main_pane(self.screen, self)


    def draw_status_bar(self):
        """Redraws the status bar."""
        
        if (self.next_message == ''):
            h, w = self.screen.getmaxyx()
            page = self.pages[self.page_index]
            start = page.start
            end = page.end
            status = 'displaying videos ' + str(start + 1) + '-' + str(end) + ' of '
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
        try:
            s = self.status_bar.getstr(0, len(prompt)).decode('utf-8')
        except KeyboardInterrupt:
            s = ''
        curses.noecho()
        curses.curs_set(0)
        return s

    
    def open_new_page(self):
        pages = self.pages
        index = self.page_index
        if (index < 1):
            index = 1
        new_page = SearchPage('search result')
        self.pages = pages[0:index + 1] + [new_page] + pages[index + 1:]
        self.page_index = max(self.page_index + 1, 2)
    
    def page_down(self):
        page = self.pages[self.page_index]
        new_start = page.end - 1
        if (new_start < len(page.videos)):
            page.start = new_start

    def page_up(self):
        page = self.pages[self.page_index]
        new_start = page.start * 2 - page.end + 1
        if (new_start > 0):
            page.start = new_start
        else:
            page.start = 0

    def close_page(self):
        index = self.page_index
        pages = self.pages
        if (index > 1):
            self.pages = pages[0:index] + pages[index + 1:]
            if (self.page_index >= len(self.pages)):
                    self.page_index -= 1

    def page_left(self):
        self.page_index = max(0, self.page_index - 1)

    def page_right(self):
        pages = self.pages
        self.page_index = min(len(pages) - 1, self.page_index + 1)

    def refresh_subs(self):
        page = self.pages[self.page_index]
        if (page.type == 'subscriptions'):
            page.refresh_subs(self.max_results)

    def do_search(self, user = False):
        index = self.page_index
        if (index < 2 and not self.open_searches_in_new_page):
            return
        prompt = 'search: ' if not user else 'search user: '
        s = self.get_input(prompt)
        if (s == ''):
            return
        if (self.open_searches_in_new_page):
            self.open_new_page()
        if (user):
            user, term = (s.split('/')[0], s.split('/')[1]) if '/' in s else (s, '')
            self.pages[self.page_index].add_search(user, term, self.user_order, self.max_results)
        else:
            self.pages[self.page_index].add_search('', s, self.search_order, self.max_results)

    def add_user(self):
        index = self.page_index
        page = self.pages[index]
        if (index == 0):
            s = self.get_input("add user: ")
            if (s == ''):
                return
            videos = search_user(s, '', self.user_order, self.max_results)
            if (videos):
                page.add_user(s)
                self.next_message = 'user ' + s + ' added to subscriptions'
            else:
                self.next_message = 'no results found for user ' + s
        elif (index == 1):
            return
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


    def loop(self):
        """The main loop of the UI."""
    
        while True:
            pages = self.pages
            index = self.page_index
            page = pages[index]
            start = page.start
            end = page.end
            c = self.status_bar.getch()
            if (c == ord('q')):
                break
            elif (c == ord('j')):
                self.page_down()
            elif (c == ord('k')):
                self.page_up()
            elif (c == ord('w')):
                self.close_page()
            elif (c == ord('n')):
                self.open_new_page()
            elif (c == ord('h')):
                self.page_left()
            elif (c == ord('l')):
                self.page_right()
            elif (c == ord('r')):
                self.refresh_subs()
            elif (c == ord('/') or c == ord('.') or c == ord(' ')):
                self.do_search()
            elif (c == ord('u')):
                self.do_search(user = True)
            elif (c == ord('s')):
                self.add_user()
            elif (c >= ord('0') and c <= ord('9')):
                input = chr(c)
                while True:
                    n = self.status_bar.getch()
                    input += chr(n)
                    if (n < ord('0') or n > ord('9')):
                        break
                num = int(input[:-1])
                command = input[-1:]
                video_index = num - 1 if self.show_real_index else num + page.start
                if (video_index >= len(page.videos)):
                    self.next_message = 'selection index out of range'
                    continue
                video = page.videos[video_index]
                if (command == 'p'):
                    self.status_bar.clear()
                    self.next_message = 'playing: ' + video.title
                    video.play(self.player, self.player_args)
                elif (command == 'b'):
                    self.pages[1].add_bookmark(video)
                    self.next_message = '"' + video.title + '" added to bookmarks'
                elif (page.type == 'bookmarks'):
                    if (command == 'k'):
                        page.swap(video, -1)
                    elif (command == 'j'):
                        page.swap(video, 1)
                    elif (command == 'd'):
                        page.delete(video) 
            self.draw_screen()


if (__name__ == '__main__'):
    try:
        ui = Ui()
        if (ui.save_session):
            if (os.path.isfile('session')):
                ui.pages, ui.page_index = pickle.load(open('session', 'rb'))
            else:
                open('session', 'a').close()
            ui.run_ui()
            pickle.dump((ui.pages, ui.page_index), open('session', 'wb'))
        else:
            ui.run_ui()
    finally:
        curses.endwin()
