from .config_parser import ConfigParser
import yaml



class YamlParser:
    def __init__(self, filename):
        self.filename = filename
        self.parse()

    def parse(self):
        f = open(self.filename, "r")
        yaml_data = yaml.safe_load(f.read())
        config = {}
        for key in yaml_data:
            config = ConfigParser.parse(key, yaml_data[key], config, self.filename)
        f.close()
        self.data = config


