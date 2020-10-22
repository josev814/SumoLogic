import ast


class ConfigParser(object):
    file = None
    config_dict = {}
    comment_starts = (';', '"', '#')

    def __init__(self, allow_no_value=False):
        if allow_no_value:
            self.allow_no_value = True

    def __getitem__(self, section):
        return self.config_dict[section]

    def read(self, file):
        config_dict = {}
        open_comment_block = False
        with open(file, 'r') as fh:
            for line in fh:
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.startswith('"""'):
                    if open_comment_block:
                        open_comment_block = False
                    else:
                        open_comment_block = True
                    continue
                if open_comment_block is False and line[0] not in self.comment_starts:
                    if line.startswith('['):
                        section = self.__parse_section(line)
                        config_dict[section] = []
                    elif line != '':
                        option_dict = self.__parse_option(line)
                        config_dict[section].append(option_dict)
                        del option_dict
                elif line[0] in self.comment_starts:
                    if section:
                        config_dict[section].append(line)
                    else:
                        config_dict['file_top'].append(line)
        self.config_dict = config_dict

    @staticmethod
    def __parse_section(line):
        if ';' in line:
            section = line.split(';')[0].strip().strip('[]')
        elif '#' in line:
            section = line.split('#')[0].strip().strip('[]')
        else:
            section = line.strip().strip('[]')
        return section

    def __parse_option(self, line) -> dict:
        key, value = line.split('=', maxsplit=1)
        val = self.__parse_value(value.strip())
        return {key.strip(): val}

    @staticmethod
    def __parse_value(value):
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        # dict
        elif value.startswith('{') and value.endswith('}'):
            value = ast.literal_eval(value)
        # list
        elif value.startswith('[') and value.endswith(']'):
            # create to dict and then pull value
            new_dict_str = '{"temp":%s}' % value
            new_dict = ast.literal_eval(new_dict_str)
            value = new_dict['temp']
            del new_dict_str
            del new_dict
        return value

    def has_section(self, section):
        if section in self.config_dict:
            return True
        return False

    def has_option(self, section, option):
        found_option = False
        if self.get_value(section, option):
            found_option = True
        return found_option

    def sections(self):
        return self.config_dict.keys()

    def get_value(self, section, option):
        value = None
        if self.has_section(section):
            print(option)
            for option_dict in self.config_dict[section]:
                if not isinstance(option_dict, str) and isinstance(option_dict, dict):
                    try:
                        if option in option_dict:
                            value = option_dict.get(option)
                            if value is not None:
                                break
                    except Exception as e:
                        import sys
                        print(sys.exc_info())
                        print(e)
                        print(option)
                        print(option_dict)
                        print(type(option_dict), end='\n\n')
                        exit(1)
        print('Returning:{}'.format(value))
        return value

    def add_section(self, section):
        if section not in self.config_dict:
            self.config_dict[section] = []

    """
    Hack to make compatible with configparser
    """
    def get(self, section, option):
        return self.get_value(section, option)

    def set(self, section, option, value):
        self.add_option(section, option, value)

    def write(self, fh):
        self.save_to_disk(fh)

    def add_option(self, section, option, value):
        if section not in self.config_dict:
            self.add_section(section)
        try:
            self.config_dict[section].append({option: value})
        except Exception:
            print('{} already exists in {}.  Use set_option to update it.'.format(option, section))
            exit(1)

    def set_option(self, section, option, value):
        if section not in self.config_dict:
            self.add_section(section)
        for idx in range(0, len(self.config_dict[section])):
            if option in self.config_dict[section][idx].keys():
                self.config_dict[section][idx][option] = value
                key_set = True
        if key_set is False:
            print('Failed to set option ({}), it doesn\'t exist'.format(option))
            exit(1)
        return True

    def options(self, section):
        options = []
        try:
            if section not in self.config_dict:
                raise ValueError
            options = self.config_dict[section]
        except ValueError:
            print("""The section, {}, doesn't exist""".format(section))
            exit(1)
        return options

    def save_to_disk(self, fh=None):
        do_close = False
        if fh is None:
            fh = open(self.file, 'w')
            do_close = True
        for config_section in self.config_dict:
            if config_section != 'file_top':
                fh.write('[{}]'.format(config_section))

            for options in self.config_dict[config_section]:
                if isinstance(options, str):
                    fh.write('{}'.format(options))
                else:
                    for key in options:
                        fh.write('{} = {}'.format(key, options[key]))
            fh.write("\n")
        if do_close:
            fh.close()
