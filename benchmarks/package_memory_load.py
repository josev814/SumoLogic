import memory_profiler
MEMDIFFS = {}
MEMTOTAL = []

packages = [
    'os',
    'time',
    'sys',
    'gzip',
    'io',
    'socket',
    'requests',
    'urllib3',
    'multiprocessing',
    'ast',
    'logging',
    'traceback',
    'configparser',
    're',
    'signal',
    'socket',
    'stat',
    'gzip',
    'bz2'
]

SumoPackages = [
    'constants',
    'daemon',
    'file_tracker',
    'jvconfigparser',
    'lockfile',
    'log_message',
    'prefs',
    'regex',
    'sumo_logic',
    'sync',
    'util'
]
SumoPackages.sort()

packages.sort()
for package in packages:
    PACKAGE_START = memory_profiler.memory_usage()
    __import__(package)
    mb = memory_profiler.memory_usage()[0] - PACKAGE_START[0]
    MEMTOTAL.append(mb)
    MEMDIFFS[package] = mb

for package in SumoPackages:
    PACKAGE_START = memory_profiler.memory_usage()
    __import__('SumoLogic.' + package)
    mb = memory_profiler.memory_usage()[0] - PACKAGE_START[0]
    MEMTOTAL.append(mb)
    MEMDIFFS[package] = mb

for pack in MEMDIFFS:
    print('{}: {} MB'.format(pack, MEMDIFFS[pack]))

print('Total Memory is ', sum(MEMTOTAL))
