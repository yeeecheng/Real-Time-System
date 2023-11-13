from .task import job, task
from .schedule import schedule
class strictSLT(schedule):
    """ smaller slack(absolute_deadline - current_time - execution_time), higher priority """
    def __init__(self):
        
        super().__init__()

    def check_preemptive_job(self):
        try:
            # preemptive
            x = self.get_current_high_priority_job()
            y = self.current_exec_job
            if (((x.absolute_deadline - self.current_time - x.remain_execution_time) < (y.absolute_deadline - self.current_time -  y.remain_execution_time)) or\
                (((x.absolute_deadline - self.current_time - x.remain_execution_time) == (y.absolute_deadline - self.current_time -  y.remain_execution_time)) and\
                    x.task.tid < y.task.tid)):
                self.__check_priority_order_ready_queue(ea_job= self.current_exec_job)
                self.locker = False
        except:
            pass
    
    def get_current_high_priority_job(self):
        self.ready_queue = sorted(self.ready_queue, key= lambda x: [(x.absolute_deadline - self.current_time - x.task.execution_time), x.task.tid])
        return self.ready_queue[0]
    
    def __check_priority_order_ready_queue(self, ea_job):

        self.ready_queue.append(ea_job)
        # sorted according to relative time & arrived time of task
        self.ready_queue = sorted(self.ready_queue, key= lambda x: [(x.absolute_deadline - self.current_time - x.task.execution_time), x.task.tid])

    def schedulability_test(self, all_tasks):
        
        res = True
        return res
    
    def dashboard(self):

        print(f"current time: {self.current_time}")
        # print(f"total job num: {self.total_job_num}")
        # print(f"miss deadline job num: {self.miss_deadline_job}")
        print(f"\nReady queue:")
        for idx, ea_job in enumerate(self.ready_queue):
            print(f"{idx}. tid: {ea_job.task.tid}, arrived_time: {ea_job.arrived_time}, slack: {(ea_job.absolute_deadline - self.current_time - ea_job.remain_execution_time)}")
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

        