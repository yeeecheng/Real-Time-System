class Job:
    def __init__(self, tid:str, period:int, exec_time:int, phase_time:int):
        self.tid = tid
        self.deadline = None
        self.remained_exec_time = exec_time
        self.period = period
        self.phase_time = phase_time

    def update_remained_exec_time(self):
        if self.remained_exec_time > 0:
            self.remained_exec_time -= 1
            return True
        return False
        

    def update_deadline(self, clock):
        self.deadline = clock + self.period