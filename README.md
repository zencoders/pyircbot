pyircbot
========

A simple python-twisted IRC. Presently pyircbot has **NOT** chat logging features. 

## Requirements

It requires the praw (Python Reddit API Wrapper) module.

## Usage

` python pyircbot.py

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
                        Channel name, default zencoders
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
