from multiprocessing import Process, current_process
import time
import sys
import os

def createdaemon(callable, kwargs):
    p = _spawn_detached(0, callable, kwargs)
    # give the process a moment to set up
    # and then kill the first child to detach
    # the second.
    time.sleep(.75)
    p.terminate()


def _spawn_detached(count, callable, kwargs):
    count += 1
    p = current_process()
    print('Process #%d: %s (%d)' % (count, p.name, p.pid))

    if count < 2:
        name = 'child'
    elif count == 2:
        try:
            # invoking a class
            name = callable.__name__
        except:
            # invoking a function
            name = callable.func_name
        sys.stdout = open(os.devnull, 'w')
    else:
        # we should now be inside of our detached process
        # so just call the function
        return callable(**kwargs)

    # otherwise, spawn another process, passing the counter as well
    p = Process(name=name, target=_spawn_detached, args=(count, callable, kwargs), daemon=False)
    p.start()
    return p
