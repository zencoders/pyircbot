import os
from ConfigParser import SafeConfigParser
from interfaces.singleton import Singleton

class ConfigManager(object):
    """ Configuration Manager Singleton class."""
    # Singleton with metaclass:
    __metaclass__ = Singleton

    def __init__(self):
        # http://stackoverflow.com/a/4060259
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.base_folder = __location__ + '/'
        config_file_path = os.path.join(__location__, 'bot.conf')
#        print "Config file path", config_file_path
        default_config_value = ["[pyircbot]\n",
                                "server = irc.freenode.net\n",
                                "port = 6667\n",
                                "channel = pyircbotroom\n",
                                "nick = pyircbot\n",
                                "greeting = 100\n",
                                "timezone = Europe/Rome\n"]
        
        # If the config file is not present try to restore it
        try:
            if not os.path.exists(config_file_path):
                conf_file = open(config_file_path, "w")
                conf_file.writelines(default_config_value)
                conf_file.close()
        except IOError, error:
            sys.exit(error)

        self._config_parser = SafeConfigParser()
        self._config_parser.readfp(open(config_file_path))
        # config options
        self._server_address = self._config_parser.get('pyircbot', 'server')
        self._server_port = self._config_parser.get('pyircbot', 'port')
        self._channel = self._config_parser.get('pyircbot', 'channel')
        self._bot_nick = self._config_parser.get('pyircbot', 'nick')
        self.greeting_probability = self._config_parser.get('pyircbot', 'greeting')
        self._timezone = self._config_parser.get('pyircbot', 'timezone')
        self._verbose = False
        self._update_data_path()

    def _update_data_path(self):
        """Internal method called to update information about data folder. Data folder path depends on channel name."""
        self._data_path = self.base_folder + self.channel + "_data/"
        self.stateful_data_path = self.base_folder + "stateful_data/"
        self.greetings_file_path = self.stateful_data_path + "greetings.txt"

    # Decorators properties
    @property
    def server_address(self):
        return self._server_address

    @server_address.setter
    def server_address(self, value):
        self._server_address = value

    @property
    def server_port(self):
        return int(self._server_port)

    @server_port.setter
    def server_port(self, value):
        self._server_port = value
    
    @property
    def channel(self):
        return self._channel 

    @channel.setter
    def channel(self, value):
        self._channel = value
        self._update_data_path()
    
    @property
    def bot_nick(self):
        return self._bot_nick

    @bot_nick.setter
    def bot_nick(self, value):
        self._bot_nick = value

    @property
    def data_path(self):
        return self._data_path

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, bool_value):
        self._verbose = bool_value

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        self._timezone = value
