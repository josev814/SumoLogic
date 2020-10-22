import linecache
import tracemalloc


class memtrace:

    def start(self):
        tracemalloc.start()

    def display_top(self, snapshot, key_type='lineno', limit=10, culmunative=False):
        snapshot = snapshot.filter_traces((
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
            tracemalloc.Filter(False, "<unknown>"),
        ))
        top_stats = snapshot.statistics(key_type, culmunative)

        print("Top %s lines" % limit)
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            print("#%s: %s:%s: %.1f KiB"
                  % (index, frame.filename, frame.lineno, stat.size / 1024))
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                print('    %s' % line)

        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))

    """
    key_type can ge filename, lineno or traceback
    culmunative can be True/False and used with filename or lineno
    """
    def stop(self, key_type='lineno', limit=10, culmunative=False):
        snapshot = tracemalloc.take_snapshot()
        if culmunative and key_type in ['lineno', 'filename']:
            self.display_top(snapshot, key_type, limit, culmunative)
        else:
            self.display_top(snapshot, key_type, limit)
