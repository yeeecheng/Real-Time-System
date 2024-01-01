from CUS import CUS, Server

class TBS(CUS):
    def __init__(self, server_size = 0.2):
        super().__init__(server_size = server_size)
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
    
    def work(self):
        
        """ update queue order"""
        self.update_priority_periodic_job_queue()
        """ whether aperiodic deadline has come """
        
        ready_periodic_job = None
        ready_aperiodic_job = self.server.get_ready_aperiodic_job()

        remove_miss_deadline_job = []
        for periodic_job in self.periodic_job_queue:
            # print(periodic_job.deadline)
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
                self.record += f"[Tid]{ready_aperiodic_job.tid} [Server Deadline]{self.server.deadline}, [Remained Exec]{ready_aperiodic_job.remained_exec_time}"
                if not self.server.consumption():
                    self.finishedAJobNumber += 1
                    # clock need to add 1, because of current clock is start time, but we need completed time(end time)
                    self.totalResponseTime += (self.clock + 1 - ready_aperiodic_job.phase_time)
                    self.record += f"\n[Response Time] {(self.clock + 1 - ready_aperiodic_job.phase_time)}({self.clock + 1} - {ready_aperiodic_job.phase_time}) [Deadline] {ready_aperiodic_job.deadline}"

        elif ready_periodic_job is not None and ready_aperiodic_job is None:
            ready_periodic_job.update_remained_exec_time()
            self.record += f"{ready_periodic_job.tid} "
            self.check_exec_time_over(job= ready_periodic_job)
        
        elif ready_periodic_job is  None and ready_aperiodic_job is not None:
            ready_aperiodic_job.update_remained_exec_time()
            self.record += f"[Tid]{ready_aperiodic_job.tid} [Server Deadline]{self.server.deadline}, [Remained Exec]{ready_aperiodic_job.remained_exec_time}"
            if not self.server.consumption():
                self.finishedAJobNumber += 1
                # clock need to add 1, because of current clock is start time, but we need completed time(end time)
                self.totalResponseTime += (self.clock + 1 - ready_aperiodic_job.phase_time)
                self.record += f"\n[Response Time] {(self.clock + 1 - ready_aperiodic_job.phase_time)}({self.clock + 1} - {ready_aperiodic_job.phase_time}) [Deadline] {ready_aperiodic_job.deadline}"

        # print info
        self.record = "No job" if self.record == "" else self.record
        self.print_current_info()


class Server(Server):
    def __init__(self, server_size = 0.2):
        super().__init__(server_size = server_size)

    def consumption(self)->bool:
        if self.ready_aperiodic_job.remained_exec_time <= 0:
            self.ready_aperiodic_job = None
            self.replenishment(rule= 3)
            return False
        self.es -=1
        return True
    

    """ update deadline and es """
    def replenishment(self, rule = 1)->bool:

        # R2
        if rule == 2:
            # current only one waiting & no job is executing
            if len(self.aperiodic_job_queue) == 1 and self.ready_aperiodic_job == None:
                
                aperiodic_job = self.aperiodic_job_queue.pop(0)
                exec_time = aperiodic_job.remained_exec_time
                self.deadline = max(self.clock, self.deadline) + exec_time / 0.2 if exec_time % 0.2 else exec_time // 0.2 + 1
                self.es = exec_time
                self.ready_aperiodic_job = aperiodic_job
                self.ready_aperiodic_job.deadline = self.deadline
        # R3
        elif rule == 3:
            if not self.aperiodic_job_queue_is_empty():
                aperiodic_job = self.aperiodic_job_queue.pop(0)
                exec_time = aperiodic_job.remained_exec_time
                self.deadline = self.deadline + exec_time / 0.2 if exec_time % 0.2 else exec_time // 0.2 + 1
                self.es = exec_time
                self.ready_aperiodic_job = aperiodic_job
                self.ready_aperiodic_job.deadline = self.deadline
                return True
