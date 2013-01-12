import os
from ConfigParser import SafeConfigParser

# TODO (sentenza) Singleton -> http://goo.gl/NArbE
class ConfigManager(object):
    def __init__(self):
        # http://stackoverflow.com/a/4060259
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self._base_path = __location__ + '/'
        _config_file_path = os.path.join(__location__, 'bot.conf')
#        print "Config file path", _config_file_path
        default_config_value = ["[default]\n",
        "server = irc.freenode.net\n",
        "port = 6667\n",
        "channel = zencoders\n",
        "nick = zenBOT"]
        
        # If the config file is not present try to restore it
        try:
            if not os.path.exists(_config_file_path):
                conf_file = open(_config_file_path, "w")
                conf_file.writelines(default_config_value)
                conf_file.close()
        except IOError, error:
            sys.exit(error)

        self._config_parser = SafeConfigParser()
        self._config_parser.readfp(open(_config_file_path))

    @property
    def server_address(self):
        return self._config_parser.get('default', 'server')

    @property
    def server_port(self):
        return self._config_parser.get('default', 'port')
    
    @property
    def channel(self):
        return self._config_parser.get('default', 'channel')
    
    @property
    def bot_nick(self):
        return self._config_parser.get('default', 'nick')

    @property
    def base_folder(self):
        return self._base_path
