pyircbot
========

A simple python-twisted IRC bot. Presently pyircbot has **NOT** chat logging features. 

## Requirements

It requires [python-twisted](http://twistedmatrix.com) and the praw (Python Reddit API Wrapper) module.

For a Debian-based Linux distribution you could install Python Twisted as follows:

```
# apt-get install python-twisted
```

Then install praw with pip:

```
$ pip install praw
```

## Usage

`$ python pyircbot.py -s irc.network.org -p 6667 -n botnickname`

```
Usage: pyircbot.py [options]
    * Basic configuration file 'bot.conf' could be used instead
    ** Information will be stored in a directory called<CHANNEL>-data

Options:
  -h, --help            show this help message and exit
  -s SERVER_ADDRESS, --server=SERVER_ADDRESS
                        IRC server address, default irc.freenode.net
  -p PORT, --port=PORT  Server port, default 6667
  -c CHANNEL, --channel=CHANNEL
                        Channel name, default mychannel
  -n NICK, --nick=NICK  Bot nickname zenbot
  -g GREETING_PROBABILITY, --greeting=GREETING_PROBABILITY
                        Greeting probability [1 - 100]
  -v, --verbose         Print a lot of stuff...
```

## Plugins

* karma and last seen
* reddit
* greetings
* diceroller
* random number
* Star Trek stardate
