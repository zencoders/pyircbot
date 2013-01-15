#! /usr/bin/env python
# Copyright (c) 2013 sentenza

"""
A simple python-twisted IRC bot with greetings and karma functionalities 
Usage:
  $ python pyircbot.py --help
"""

import sys
import optparse
from config import ConfigManager
from bot_core.bot_factory import BotFactory

if __name__ == '__main__':
    config_manager = ConfigManager()
    usage = """usage: %prog [options]
    * Basic configuration file 'bot.conf' could be used instead
    ** Information will be stored in a directory called<CHANNEL>-data"""
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--server", dest="server_address",
                    action="store",
                    default = config_manager.server_address,
                    help="IRC server address, default %s" % config_manager.server_address)
    parser.add_option("-p", "--port", dest="port",
                    action="store",
                    type="int",
                    default = config_manager.server_port,
                    help="Server port, default %s" % config_manager.server_port)   
    parser.add_option("-c", "--channel", dest="channel",
                    action="store",
                    type="string",
                    default = config_manager.channel,
                    help="Channel name, default %s" % config_manager.channel)
    parser.add_option("-n", "--nick", dest="nick",
                    action="store",
                    default = config_manager.bot_nick,
                    help="Bot nickname %s" % config_manager.bot_nick)
    parser.add_option("-g", "--greeting", dest="greeting_probability",
                    action="store",
                    type="int",
                    default = 30,
                    help="Greeting probability [1 - 100]")
    parser.add_option("-v", "--verbose", dest="verbose",
                    action="store_true",
                    help="Print a lot of stuff...")

 
    options, args = parser.parse_args()

    # Set options to ConfigManager
    config_manager.server_address = options.server_address
    config_manager.server_port = options.port
    config_manager.channel = options.channel
    config_manager.bot_nick = options.nick
    config_manager.verbose = options.verbose
    config_manager.greeting_probability = options.greeting_probability

    #if not options.<something>:
    #    parser.error('Must choose one option try -n or -c or --help')

    if config_manager.verbose:
        print "Information will be stored in ", config_manager.data_path
    
    factory = BotFactory()
    factory.connect()
    factory.run()
