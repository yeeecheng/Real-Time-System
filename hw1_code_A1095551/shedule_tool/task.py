class task:

    def __init__(self, phase_time, period, relative_deadline, execution_time, tid):

        self.tid = tid
        self.phase_time = int(phase_time)
        self.period = int(period)
        self.relative_deadline = int(relative_deadline)
        self.execution_time = int(execution_time)
        
    def set_tid(self, tid):
        self.tid = tid

    

class job:

    def __init__(self, task, current_time, release_time = None, remain_execution_time = None, absolute_deadline = None):

        self.task = task
        self.arrived_time = current_time 
        self.release_time = release_time 
        self.remain_execution_time = remain_execution_time
        self.absolute_deadline = absolute_deadline

    def set_job(self, release_time):

        self.release_time = release_time
        self.absolute_deadline = self.release_time + self.task.relative_deadline
        self.remain_execution_time = self.task.execution_time

    def update_remain_execution_time(self):
        self.remain_execution_time -= 1
    
    
