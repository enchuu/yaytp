yaytp
=====

Command line tool to browse youtube with ncurses

dependencies: mpv, python3

usage: run ui.py with 'python3 ui.py' or './ui.py'

there are 2 special pages: subscriptions and bookmarks
subscriptions are like channel subscriptions, it displays a list of uploads by users added to the subscription list sorted by date uploaded
bookmarks are a list of videos added from either the subscription list or search results
everything else is a search page, you can search for terms or users


customization options:
there aren't really that many, if you want to change stuff you can look at the source code.
must of the stuff is in init of ui.py
formatting stuff is in draw methods of ui.py
make an issue request if you really want to change something and don't know how


keybinds:
navigation:hjkl
make a new page:n
close a page:w
start a search:/ space or .
start a search for a user:u (user/term will search for videos with term in user's uploads)
play a video:[number]p
add a video to bookmarks:[number]b
deleting a a video in the bookmarks page:[number]d
moving up/down a video in the bookmarks page:[number]:k/j
add a user to subscriptions:s
quit:q


todo:
organize page class better
fix hackish code
dynamically change settings without editing source
maybe add a download option? would require yt-dl
maybe allow for custom locations/amounts of bookmarks/subscriptions pages?
