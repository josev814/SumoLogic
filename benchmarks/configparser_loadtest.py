from memtrace import memtrace
mt = memtrace()
mt.start()

from configparser import ConfigParser


def print_regular_configparser():
    cp = ConfigParser(allow_no_value=True)
    ucp = ConfigParser(allow_no_value=True)
    cp.read(r'../default_config')
    ucp.read(r'../user_config')
    if cp.has_section('default'):
        print('Good')
    if cp.has_option('default', 'debug'):
        print('Good')
    if ucp.has_section('default'):
        print('Good')
    if ucp.has_option('default', 'debug'):
        print('Good')
    print(cp.get('default', 'debug'))
    # print(cp.get_value('default', 'debug'))
    print(ucp.get('default', 'debug'))
    # print(ucp.get_value('default', 'debug'))
    for section in cp.sections():
        print(section)
        print(cp.options(section))
    # print(cp.config_dict)
    for section in ucp.sections():
        print(section)
        print(ucp.options(section))
    # print(ucp.config_dict)
    ucp.add_section('Jose')
    ucp.set('Jose', 'test', 'hello')
    # ucp.add_option('Jose', 'test', 'hello')
    print(ucp.get('Jose', 'test'))
    # print(ucp.get_value('Jose', 'test'))
    ucp.set('Jose', 'test', 'jello')
    # ucp.set_option('Jose', 'test', 'jello')
    print(ucp.get('Jose', 'test'))
    # print(ucp.get_value('Jose', 'test'))
    for config_section in ucp.sections():
        print('[', config_section, ']', sep='')
        for options in ucp.options(config_section):
            if isinstance(options, str):
                print(options)
            else:
                print(options)
                for key in options:
                    print('{} = {}'.format(key, options[key]))


if __name__ == '__main__':
    print_regular_configparser()
    mt.stop('filename', limit=20)

