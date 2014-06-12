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
settings can be changed by editing the Settings class in ui.py, or on the fly by typing s in the prompt


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
filter a current page for a term:f, then the term  
change a setting:c, then [setting]=[value], no spaces between the '='  
quit:q  

