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


  def add_search(self, user, term, ordering, max_results):
    """Performs a search on a search page."""

    assert self.type == 'search result', 'cannot add a search to a non-search page'
    self.user = user
    self.term = term
    self.ordering = ordering
    self.max_results = max_results
    if (user != ''):
      self.videos = search_user(user, term, ordering, max_results)
    else:
      self.videos = search_term(term, ordering, max_results)


  def add_bookmark(self, video):
    """Adds a bookmark to a bookmark page."""

    assert self.type == 'bookmarks', 'cannot add a bookmark to a non-bookmark page'
    self.videos.append(video)


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


  def swap(self, video, shift):
    index = self.videos.index(video)
    if ((index == 0 and shift < 0) or (index == len(self.videos) - 1 and shift > 0)):
      return
    else:
      self.videos[index + shift], self.videos[index] = self.videos[index], self.videos[index + shift]
   
  def delete(self, video):
    index = self.videos.index(video)
    self.videos = self.videos[:index] + self.videos[index + 1:]
