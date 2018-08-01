from builtins import super

import gdocrevisions

from timeit import default_timer as timer


def timeit(method):
    """
    Decorator for timing an instance method and recording elapsed time in self.times (dict)
    """
    def timed(*args, **kwargs):
        start = timer()
        result = method(*args, **kwargs)
        stop = timer()
        # args[0] is self
        args[0].times[method.__name__] = stop-start
        return result

    return timed


class TimedDoc(gdocrevisions.GoogleDoc):
    """
    Time the following GoogleDoc methods:
    1. _download_revision_details()
    2. _build_revisions()
    3. _apply_all_revisions()

    Execution times get stored in self.times dict
    """
    def __init__(self, *args, **kwargs):
        # used to store execution times for performance testing
        self.times = {}
        return super().__init__(*args, **kwargs)

    @timeit
    def _download_revision_details(self):
        return super(TimedDoc, self)._download_revision_details()

    @timeit
    def _build_revisions(self):
        return super(TimedDoc, self)._build_revisions()

    @timeit
    def _apply_all_revisions(self):
        return super(TimedDoc, self)._apply_all_revisions()
