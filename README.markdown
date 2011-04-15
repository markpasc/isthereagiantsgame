# Is there a Giants game? #

A single serving web site for whether there's a game of San Francisco
Giants baseball on a day.

See it at [isthereagiantsga.me](http://isthereagiantsga.me/).

## Other days ##

You can ask about some other days besides today by including that day in
the URL. For example, go to `http://isthereagiantsga.me/tomorrow` to see
if there's a game tomorrow. Days you can use are:

* `today`
* `tomorrow`
* a day of the week such as `tuesday`; the current day of the week
  refers to that day *next* week
* a numeric date in `YYYYMMDD` format

## API ##

Is there a Giants game? provides an API at:

    http://isthereagiantsga.me/api/<day>

For *day* specify the day you're inquiring about, as on the regular
website. (Unlike the web site, you *must* specify `today` to find out if
there's a game today.)

The status code of the response shows whether there's a game that day:

* `200 OK`: there is a game that day
* `204 No Content`: there is a game, but it's an away game
* `404 Not Found`: there is not a game that day
