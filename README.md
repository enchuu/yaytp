yaytp
=====

Command line tool to browse youtube with ncurses
Doesn't currently work right now

dependencies: mpv, python3

usage: run ui.py

keybinds:

navigation:hjkl
make a new page:n
close a page:w
start a search:/ space or .
start a search for a user:u (user/term will search for videos with term in user's uploads)
play a video:[number]p
add a video to bookmarks:[number]b
add a user to subscriptions:s
quit:q

todo:
organize page class better
add colors
fix exceptions crashing everything
add some options
figure out how to save settings/state
fix hackish code
