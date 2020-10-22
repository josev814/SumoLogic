# 273.8Kb Total
from memtrace import memtrace

mt = memtrace()
mt.start()

from SumoLogic.sumo_logic import SumoConfig

if __name__ == '__main__':
    sc = SumoConfig('default_config', 'user_config')
    print(sc.get_active_log_files())
    mt.stop(key_type='filename', limit=40, culmunative=True)
