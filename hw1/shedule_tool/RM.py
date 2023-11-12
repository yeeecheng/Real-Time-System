from .task import job, task
from .schedule import schedule
class RM(schedule):
    """ smaller period, higher priority """
    def __init__(self):
        
        super().__init__()

    def __check_priority_order_ready_queue(self, ea_job):

        self.ready_queue.append(ea_job)
        # sorted according to relative time & arrived time of task
        self.ready_queue = sorted(self.ready_queue, key= lambda x: [x.task.period, x.arrived_time])

    def schedulability_test(self, all_tasks):

        utilized_rate = 0
        for task in all_tasks:
            utilized_rate += task.execution_time / min(task.period, task.relative_deadline)
        
        n = len(all_tasks)
        return utilized_rate <= n * pow(2, 1 / n) - 1
    
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
            print(f"\ntid: {cur_exec_job.task.tid}")
            print(f"release_time: {cur_exec_job.release_time}")
            print(f"absolute_deadline: {cur_exec_job.absolute_deadline}")
            print(f"remain_execute_time: {cur_exec_job.remain_execution_time}")
            self.record_schedule.append([self.current_time, f"T{cur_exec_job.task.tid}"])
        except:
            print("no job executing")
            self.record_schedule.append([self.current_time, "no job"])
        print("\n")