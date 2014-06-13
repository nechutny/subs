subs
====

Subtitle downloader for video files from opensubtitles.org


How use it?
====

Basic usage is:
$./subs.py ../Movies/movie.avi

Default language for searched subtitles is English (eng), but you can specify language, for example:
$./subs.py -l cze ../Movies/movie.avi

You can also download at once subtitles for more files:
$./subs.py ../Movies/movie1.avi ../Movies/movie2.avi

or via bash expansion:
$./subs.py ../Movies/*.avi

and of course you can combine it with -l lang argument.
