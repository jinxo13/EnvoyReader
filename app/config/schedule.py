from datetime import timedelta
from celery.schedules import schedule

class ScheduleOffset(schedule):
    def __init__(self, run_every=None, offset=None):
        self._run_every = run_every
        self._offset = offset if offset is not None else timedelta(seconds=0)
        self._do_offset = True if self._offset else False
        super(ScheduleOffset, self).__init__(
            run_every=self._run_every + self._offset)

    def is_due(self, last_run_at):
        ret = super(ScheduleOffset, self).is_due(last_run_at)
        if self._do_offset and ret.is_due:
            self._do_offset = False
            self.run_every = self._run_every
            ret = super(ScheduleOffset, self).is_due(last_run_at)
        return ret

    def __reduce__(self):
        return self.__class__, (self._run_every, self._offset)