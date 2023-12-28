import logging
from job import Job


""" Base on EDF schedule"""
class CUS:

    def __init__(self, server_size = 0.2):
        self.periodic_job_queue = list()
        self.server = Server(server_size = server_size)
        self.clock = 0
        # requirement
        self.totalPjobNumber = 0
        self.missPjobNumber = 0
        self.finishedAJobNumber = 0
        self.totalResponseTime = 0

        # Record
        self.record = ""
        self.all_record = ""
        
    def arriving_new_job(self, periodic_jobs: list, aperiodic_jobs: list):
        
        self.record = ""

        for periodic_job in periodic_jobs:
            self.totalPjobNumber += 1
            periodic_job.update_deadline(clock= self.clock)
            
            if self.check_miss_deadline(periodic_job):
                self.missPjobNumber += 1
                continue
            self.periodic_job_queue.append(periodic_job)
        if len(aperiodic_jobs) != 0:
            self.server.arriving_new_aperiodic_job(aperiodic_jobs= aperiodic_jobs)

    def work(self):
        
        """ update queue order"""
        self.update_priority_periodic_job_queue()
        """ whether aperiodic deadline has come """
        self.server.replenishment(rule= 3)
        ready_periodic_job = None
        ready_aperiodic_job = self.server.get_ready_aperiodic_job()

        remove_miss_deadline_job = []
        for periodic_job in self.periodic_job_queue:
            if self.check_miss_deadline(periodic_job):
                remove_miss_deadline_job.append(periodic_job)
            
        for periodic_job in remove_miss_deadline_job:
            self.periodic_job_queue.remove(periodic_job)
        
        ready_periodic_job = self.periodic_job_queue[0] if len(self.periodic_job_queue) else None
        
        # There are aperiodic job and periodic job 
        if ready_periodic_job is not None and  ready_aperiodic_job is not None:
            # periodic job  work first
            if ready_periodic_job.deadline < self.server.deadline:
                ready_periodic_job.update_remained_exec_time()
                self.record += f"{ready_periodic_job.tid} "
                self.check_exec_time_over(job= ready_periodic_job)
            else:
                ready_aperiodic_job.update_remained_exec_time()
                self.record += f"{ready_aperiodic_job.tid} "
                if not self.server.consumption():
                    self.finishedAJobNumber += 1
                    # clock need to add 1, because of current clock is start time, but we need completed time(end time)
                    self.totalResponseTime += (self.clock + 1 - ready_aperiodic_job.phase_time)
        
        elif ready_periodic_job is not None and ready_aperiodic_job is None:
    
            ready_periodic_job.update_remained_exec_time()
            self.record += f"{ready_periodic_job.tid} "
            self.check_exec_time_over(job= ready_periodic_job)
        
        elif ready_periodic_job is  None and ready_aperiodic_job is not None:
            ready_aperiodic_job.update_remained_exec_time()
            self.record += f"{ready_aperiodic_job.tid} "
            if not self.server.consumption():
                self.finishedAJobNumber += 1
                # clock need to add 1, because of current clock is start time, but we need completed time(end time)
                self.totalResponseTime += (self.clock + 1 - ready_aperiodic_job.phase_time)

        # print info
        self.record = "No job" if self.record == "" else self.record
        self.print_current_info()

    """arrange all periodic job by absolute deadline"""
    def update_priority_periodic_job_queue(self):
        self.periodic_job_queue = sorted(self.periodic_job_queue, key= lambda x: [x.deadline,int(x.tid[1:])])
        
    def update_clock(self, current_clock):
        self.clock = current_clock
        self.server.update_clock(current_clock= current_clock)

    def check_exec_time_over(self, job):
    
        if job.remained_exec_time <= 0:
            self.periodic_job_queue.pop(0)
            
    """ check whether miss deadline"""
    def check_miss_deadline(self, job: Job)->bool:
        
        if (job.deadline - self.clock - job.remained_exec_time) <= 0:
            self.missPjobNumber += 1
            self.record += f"{job.tid} miss deadline "
            return True
        return False

    def print_current_info(self):
        # print(f"{self.clock} {self.record}")
        self.all_record += f"{self.clock} {self.record}\n"

    def print_output(self):
        print(f"missPjobNumber: {self.missPjobNumber}")
        print(f"totalPjobNumber: {self.totalPjobNumber}")
        print(f"totalResponseTime: {self.totalResponseTime}")
        print(f"finishedAJobNumber: {self.finishedAJobNumber}")
        print(f"Miss Rate: {self.missPjobNumber / self.totalPjobNumber}")
        print(f"Average Response Time: {self.totalResponseTime / self.finishedAJobNumber}")
        self.all_record += f"missPjobNumber: {self.missPjobNumber}\n"
        self.all_record += f"totalPjobNumber: {self.totalPjobNumber}\n"
        self.all_record += f"totalResponseTime: {self.totalResponseTime}\n"
        self.all_record += f"finishedAJobNumber: {self.finishedAJobNumber}\n"
        self.all_record += f"Miss Rate: {self.missPjobNumber / self.totalPjobNumber}\n"
        self.all_record += f"Average Response Time: {self.totalResponseTime / self.finishedAJobNumber}\n"

    def save(self, save_path):
        with open(save_path, "w", encoding= "utf-8") as f:
            f.write(self.all_record)
    
class Server:

    def __init__(self, server_size = 0.2):
        
        self.server_size = server_size
        """
        current aperiodic job queue with FIFO Rule
        """
        self.aperiodic_job_queue = list()
        # not yet choose
        self.ready_aperiodic_job = None
        self.clock = 0
        # current_job deadline
        self.deadline = 0
        # budgets
        self.es = 0

    def update_clock(self, current_clock):
        self.clock = current_clock

    def aperiodic_job_queue_is_empty(self):
        return False if len(self.aperiodic_job_queue) else True
    

    def arriving_new_aperiodic_job(self, aperiodic_jobs):
        for aperiodic_job in aperiodic_jobs:
            self.aperiodic_job_queue.append(aperiodic_job)
            # first job first replenishment
            self.replenishment(rule= 2)

    def get_ready_aperiodic_job(self):

        return self.ready_aperiodic_job
    
    def consumption(self)->bool:
        if self.ready_aperiodic_job.remained_exec_time <= 0:
            self.ready_aperiodic_job = None
            return False
        self.es -=1
        return True
    
    """ update deadline and es """
    def replenishment(self, rule = 1)->bool:

        if rule == 2:
            if len(self.aperiodic_job_queue) == 1 and self.ready_aperiodic_job == None:
                if self.clock >= self.deadline:

                    aperiodic_job = self.aperiodic_job_queue.pop(0)
                    exec_time = aperiodic_job.remained_exec_time
                    self.deadline = self.clock + exec_time / 0.2 if exec_time % 0.2 else exec_time // 0.2 + 1
                    self.es = exec_time
                    self.ready_aperiodic_job = aperiodic_job
        elif rule == 3:
            if self.clock == self.deadline:
                if not self.aperiodic_job_queue_is_empty():
                    aperiodic_job = self.aperiodic_job_queue.pop(0)
                    exec_time = aperiodic_job.remained_exec_time
                    self.deadline = self.deadline + exec_time / 0.2 if exec_time % 0.2 else exec_time // 0.2 + 1
                    self.es = exec_time
                    self.ready_aperiodic_job = aperiodic_job
                else:
                    self.es = 0
                    self.ready_aperiodic_job = None
