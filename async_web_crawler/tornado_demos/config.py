import derpconf.config as config 
from derpconf.config import Config

#Config.define('MY-KEY', 'DEFAULT VALUE', 'Description for my key', 'Section')
Config.define('PORT', '12345', 'Listened port', 'Application')
Config.define('TEMPLATE_DIR', '.', 'tempalte files directory', 'Template')
Config.define('DATABASE', 'database-demo', 'unuseful, just for demo', 'Useless')


if __name__ == '__main__':
    config.generate_config()


