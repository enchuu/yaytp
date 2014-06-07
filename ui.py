#!/usr/bin/env python3

import curses
import math
from format import *
from page import *
from query import *
from video import *

class Ui():
  """The main Ui."""

  def __init__(self):
    self.max_results = 20
    self.info_width = 23
    self.user_order = 'published'
    self.search_order = 'relevance'
    self.player = 'mpv'
    self.player_args = ''
    self.pages = []
    self.next_message = ''
    self.pages.append(Page('subscriptions'))
    self.pages.append(Page('bookmarks'))
    self.pages.append(Page('search result'))
    self.page_index = 2
    self.run_ui()


  def run_ui(self):
    """Sets up the ncurses interface."""

    self.screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    self.draw_screen()
    self.loop()


  def draw_screen(self):
    """Redraws the entire screen."""

    h, w = self.screen.getmaxyx()
    info_pane_start = w - self.info_width
    self.main_pane = curses.newwin(h-2, info_pane_start, 0, 1)
    self.info_pane = curses.newwin(h-2, self.info_width, 0, info_pane_start)
    self.page_bar = curses.newwin(1, w, h - 2, 0)
    self.status_bar = curses.newwin(1, w, h - 1, 0)
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
      status = 'Displaying videos ' + str(start) + '-' + str(end) + ' of '
      if (page.type == 'search result'):
        if (not page.videos and not hasattr(page, 'user')):
          status = 'new page'
        elif (not page.videos):
          status = 'no results found'
        elif (page.user == ''):
          status += 'a search for "' + page.term + '" ordered by ' + page.ordering
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
    if (page.type == 'subscriptions'):
      page.refresh_subs(self.max_results)
    start = page.start
    h, w = pane.getmaxyx()
    videos_per_page = h // 3
    end = min(len(page.videos), start + videos_per_page)
    y = 0
    for video in page.videos[start:end]:
      title, desc = video.format_title_desc(y // 3)
      pane.addstr(y, 0, title)
      info_pane.addstr(y, 0, video.format_info())
      y += 1
      pane.addstr(y, 0, desc)
      y += 2
    pane.refresh()
    info_pane.refresh()


  def draw_page_bar(self):
    """Redraws the page bar."""

    pages = self.pages
    current = self.page_index
    panel = self.page_bar
    h, w = panel.getmaxyx()
    prev = ''
    bar = '---[' + pages[current].format() + ']---'
    i = 1
    while (len(bar) < w and (current - i >= 0 or current + i < len(pages))):
      prev = bar
      bar = '----' + pages[current - i].format() + '----' + bar if current  - i >= 0 else bar
      bar = bar + '----' + pages[current + i].format() + '----' if current  + i < len(pages) else bar
      i += 1
    if (len(bar) > w - 3):
      bar = prev
    while (get_real_width(bar) < w - 3):
      bar = '-' + bar + '-'
    if (get_real_width(bar) < w - 1):
      bar += '-'
    panel.addstr(0, 0, bar)
    panel.refresh()


  def get_input(self, prompt):
    """Gets input for a search."""

    curses.echo()
    self.status_bar.erase()
    self.status_bar.addstr(0, 0, prompt)
    self.status_bar.refresh()
    s = self.status_bar.getstr(0, len(prompt)).decode('utf-8')
    curses.noecho()
    return s


  def loop(self):
    """The main loop of the UI."""
  
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
        if (index > 0):
          new_page = Page('search result')
          self.pages = pages[0:index + 1] + [new_page] + pages[index + 1:]
          self.page_index += 1
      elif (c == ord('h')):
        self.page_index = max(0, self.page_index - 1)
      elif (c == ord('l')):
        self.page_index = min(len(pages) - 1, self.page_index + 1)
      elif (c == ord('/') or c == ord('.') or c == ord(' ')):
        s = self.get_input("search: ")
        page.add_search('', s, self.search_order, self.max_results)
      elif (c == ord('s')):
        if (index == 0):
          s = self.get_input("add user: ")
          videos = search_user(s, '', self.user_order, self.max_results)
          if (videos):
            page.add_user(s)
            self.next_message = 'user ' + s + ' added to subscriptions'
          else:
            self.next_message = 'no results found for user ' + s
        else:
          if (not hasattr(page, 'user')):
            self.next_message = 'not a user search page'
          else:
            s = page.user
            if (page.videos):
              self.pages[0].add_user(s)
              self.next_message = 'user ' + s + ' added to subscriptions'
            else:
              self.next_message = 'no results found for user ' + s
      elif (c == ord('u')):
        s = self.get_input("search user: ")
        user, term = (s.split('/')[0], s.split('/')[1]) if '/' in s else (s, '')
        page.add_search(user, term, self.user_order, self.max_results)
      elif (c >= ord('0') and c <= ord('9')):
        n = self.status_bar.getch()
        video = page.videos[page.start + c - ord('0')]
        if (n == ord('p') or n == 13):
          self.status_bar.clear()
          self.status_bar.addstr(0, 0, 'playing: ' + video.title)
          self.status_bar.refresh()
          video.play(self.player, self.player_args)
        elif (n == ord('b')):
          self.pages[1].add_bookmark(video)
      self.draw_screen()
    curses.endwin()


ui = Ui()
