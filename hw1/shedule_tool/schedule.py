from .task import job, task

class schedule:
    """ smaller period, higher priority """
    def __init__(self):
        
        self.ready_queue = list()
        self.total_job_num = 0
        self.miss_deadline_job = 0
        self.locker = False
        self.current_time = 0
        self.record_schedule = []
    
    def reset(self):
        self.ready_queue = list()
        self.total_job_num = 0
        self.miss_deadline_job = 0
        self.locker = False
        self.current_time = 0
        self.record_schedule = []
        try:
            del self.current_exec_job
        except:
            pass

    def check_current_exec_job_state(self):
        self.current_exec_job.update_remain_execution_time()
        # executive time is over
        if self.current_exec_job.remain_execution_time <= 0:
            return False
        # still executing
        return True

    def check_miss_deadline_job(self):
        # check whether there is enough time to execute
        miss_deadline_val = []
        for job in self.ready_queue:
            if (job.absolute_deadline - self.current_time - job.remain_execution_time) < 0:
                print("miss")
                if len(self.record_schedule) != 0 and self.record_schedule[-1][0] == self.current_time:
                    self.record_schedule[-1].append(f"T{job.task.tid} miss deadline")
                else:
                    self.record_schedule.append([self.current_time, f"T{job.task.tid} miss deadline"])
                self.miss_deadline_job += 1
                
                miss_deadline_val.append(job)
        
        for need_remove_job in miss_deadline_val:
            self.ready_queue.remove(need_remove_job)

    def check_execution_phase(self):
        
        # no job is executing and there are job in the ready queue.
        if not self.locker and len(self.ready_queue) > 0: 
            
            self.current_exec_job = self.get_current_high_priority_job()
            self.ready_queue.pop(0)
            
            self.locker = True
        
        self.dashboard()
        
        # already during the execution phase
        if self.locker:
            # executive time is over
            if not self.check_current_exec_job_state():
                self.locker = False
                del self.current_exec_job

    # diff
    def check_preemptive_job(self):
        try:
            # preemptive
            if self.get_current_high_priority_job().task.period < self.current_exec_job.task.period:
                self.__check_priority_order_ready_queue(ea_job= self.current_exec_job)
                self.locker = False
        except:
            pass

    def get_current_high_priority_job(self):

        return self.ready_queue[0]
    
    def update_time(self, current_time):
        self.current_time = current_time

    def check_locker(self, current_time):
        pass
    
    # diff
    def __check_priority_order_ready_queue(self, ea_job):

        self.ready_queue.append(ea_job)
        # sorted according to relative time & arrived time of task
        self.ready_queue = sorted(self.ready_queue, key= lambda x: [x.task.period, x.arrived_time])

    def get_new_task(self, task):
        self.total_job_num += 1
        ea_job = job(task= task, current_time= self.current_time)
        ea_job.set_job(release_time= self.current_time)
        self.__check_priority_order_ready_queue(ea_job= ea_job)

    # diff
    def schedulability_test(self, all_tasks):

        utilized_rate = 0
        for task in all_tasks:
            utilized_rate += task.execution_time / min(task.period, task.relative_deadline)
        
        n = len(all_tasks)
        res = utilized_rate <= n * (pow(2, 1 / n) - 1)
        if not res:
            self.record_schedule.append("May not schedule")
        return res
    
    def dashboard(self):

        print(f"current time: {self.current_time}")
        print(f"total job num: {self.total_job_num}")
        print(f"miss deadline job num: {self.miss_deadline_job}")
        print(f"\nReady queue:")
        for idx, ea_job in enumerate(self.ready_queue):
            print(f"{idx}. tid: {ea_job.task.tid}, arrived_time: {ea_job.arrived_time}, period: {ea_job.task.period}")
        print("\ncurrent execution job: ", end ="")
        try:
            cur_exec_job = self.current_exec_job
            print(f"\ntid: {cur_exec_job.task.tid}", end =", ")
            print(f"release_time: {cur_exec_job.release_time}", end =", ")
            print(f"absolute_deadline: {cur_exec_job.absolute_deadline}", end =", ")
            print(f"remain_execute_time: {cur_exec_job.remain_execution_time}")
            if len(self.record_schedule) != 0 and self.record_schedule[-1][0] == self.current_time:
                self.record_schedule[-1].insert(1, f"T{cur_exec_job.task.tid}")
            else:
                self.record_schedule.append([self.current_time, f"T{cur_exec_job.task.tid}"])
        except:
            print("no job executing")
            if len(self.record_schedule) != 0 and self.record_schedule[-1][0] == self.current_time:
                self.record_schedule[-1].insert(1, "no job")
            else:
                self.record_schedule.append([self.current_time, "no job"])
        print("\n")
        

    def print_record(self, save_path = None):
        data = ""
        for record in self.record_schedule:
            if len(record) == 1:
                print(f"{record[0]}")
                data += f"{record[0]}\n"
            elif len(record) != 2:
                miss_deadline_info = ""
                for idx in range(2, len(record)):
                    miss_deadline_info += record[idx] + ", "
                miss_deadline_info = miss_deadline_info.strip(", ")
                print(f"{record[0]} {record[1]} ({miss_deadline_info})")
                data += f"{record[0]} {record[1]} ({miss_deadline_info})\n"
            else:
                print(f"{record[0]} {record[1]}")
                data += f"{record[0]} {record[1]}\n"

        with open(save_path, "w", encoding= "utf-8") as f:
            f.write(data)