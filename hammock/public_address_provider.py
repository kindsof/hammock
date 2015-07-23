import netaddr
import ConfigParser
import os


class PublicAddressProvider(object):
    _ANSWER_FILE_PATH = '/etc/stratoscale/answerfile.ans'

    @staticmethod
    def get_public_ip(config_source=_ANSWER_FILE_PATH):

        config = ConfigParser.RawConfigParser()
        if isinstance(config_source, str):
            if os.path.exists(config_source):
                config.read(config_source)
            else:
                raise ValueError('config file "{}" does not exist.'.format(config_source))
        else:
            config.readfp(config_source)
        if config.has_section('general') and config.has_option('general', 'accessaddress'):
            address = config.get('general', 'accessaddress')
            ip = netaddr.IPNetwork(address)
            return ip.ip
        return None
