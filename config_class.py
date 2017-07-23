import os
import yaml


def load_test_config(config_file='config.yaml'):
    """
    Loaf tes config from config.yaml file
    :param config_file: config file name
    :return: yaml config
    """
    package_root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(package_root, config_file)
    try:
        with open(path) as f:
            config = yaml.load(f)
    except IOError:
        config = None
    return config


class Config:
    """
    Config class instansiates yaml configuration
    """
    def __init__(self):
        self.app = None
        config = load_test_config()
        for key in config:
            setattr(self, key, config[key])
