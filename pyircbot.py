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
    ** Basic configuration file 'bot.conf' could be used instead"""
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--server", dest="server",
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
    # TODO (sentenza) use the config manager class
    parser.add_option("-v", "--verbose", dest="verbose",
                    action="store_true",
                    help="Print a lot of stuff...")
    options, args = parser.parse_args()

    # TODO (sentenza) Check the possibility of writing the config file via optparse args
    #if not options.network and not options.channel:
    #    parser.error('Must choose one-- try -n or -c')

    data_path = config_manager.base_folder + options.channel + "-data/"
    if options.verbose:
        print "Storing BOT data in ", data_path
    
    # Building the factory and passing the Protocol as the second argument
    factory = BotFactory(options.channel, options.nick, data_path)
    factory.connect(options.server, options.port)
    factory.run()
