subs
====

Subtitle downloader for video files from opensubtitles.org


How use it?
====

Basic usage is:

    $./subs.py ../Movies/movie.avi

Default language for searched subtitles is system language. If it can't detect, then it fall to English (eng), but you can specify language, for example:

    $./subs.py -l cze ../Movies/movie.avi
  
Subtitles are default downloaded to same directory as is movie. -d directory argument allow download them to custom directory.

    $./subs.py -d /mnt/subtitles/ ../Movies/movie.avi

You can also download at once subtitles for more files:

    $./subs.py ../Movies/movie1.avi ../Movies/movie2.avi

or via bash expansion:

    $./subs.py ../Movies/*.avi
    
And what about removing advertisement in subtitles (annonying link etc.)? Just use (experimental) -a argument

    $./subs.py -a ../Movies/*.avi

and of course you can combine it with -l lang, or -d directory argument.
