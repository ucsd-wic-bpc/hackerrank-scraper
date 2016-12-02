hackerrank-scraper
==================
A tool made to get leader information from a currently running Hackerrank 
competition's ACM-style leaderboard.


Installation/Use
----------------
On it's own, `hackerrank-scraper` is a library. It's usage is exercised in the
included sample program, `hr.py`. Of course, a valid `config.json` is required
to use `hr.py`.

By default, `hackerrank-scraper` uses [PhantomJS](https://github.com/ariya/phantomjs/)
to scrape the leaderboards. Thus, PhantomJS should be installed and in your
path. Otherwsie, provide an alternative selenium webdriver when constructing
the Scraper object


1. `pip install -r requirements.txt`  
2. Fill config.json  
3. python hr.py
