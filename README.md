==========
SortIt-app
==========

Rate things by draging and droping them! Deployed app can be tested here: http://granite.dy.fi/jafna/sortit

Requirements
------------

* Flask ( pip install Flask )
* Flask-And-Redis ( pip install Flask-And-Redis )
* Flask-Testing ( pip install Flask-Testing )
* Flask-Script ( pip install Flask-Script)
* Nose (pip install nose)

Run
===

First load base data (contains small set of movielens data and a base category). Even with quite small dataset this will take ~10mins.
Be aware that init runs flushall for redis instance!

```
$ python manage.py init
```

Run server
```
$ python manage.py run
```
Direct your browser to: 127.0.0.1:5000

To-Do
=====
* Have recommendations for users
* Users to have ability to paste URLs
* More test coverage!
