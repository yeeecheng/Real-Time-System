from TBS import TBS
from CUS import CUS
from job import Job
import copy


class simulation:

    def __init__(self, periodic_file_path, aperiodic_file_path, scheduler):
        
        self.maxSimTime = 1000
        self.clock_start_time = 0
        self.periodic_jobs = []
        self.aperiodic_jobs = []
        # setting scheduler
        self.scheduler = TBS() if scheduler == "TBS" else CUS()
        self.__load_file(periodic_file_path= periodic_file_path, aperiodic_file_path= aperiodic_file_path)

    def __load_file(self, periodic_file_path, aperiodic_file_path):
        
        periodic_tid = 1
        # load periodic jobs
        with open(periodic_file_path, "r") as f:
            for task in f.readlines(): 
                period, exec_time = task.split(",")
                self.periodic_jobs.append(
                    Job(tid= f"T{periodic_tid}", 
                        period= int(period), 
                        exec_time= int(exec_time),
                        phase_time= 0)
                    )
                periodic_tid += 1
        f.close()
        # arrange by period 
        self.periodic_jobs = sorted(self.periodic_jobs, key= lambda x: x.period)

        aperiodic_tid = 1
        # load aperiodic jobs
        with open(aperiodic_file_path, "r") as f:
            for task in f.readlines():
                phase_time, exec_time = task.split(",")
                self.aperiodic_jobs.append(
                    Job(tid= f"A{aperiodic_tid}", 
                        period= None, 
                        exec_time= int(exec_time),
                        phase_time= int(phase_time))
                    )
                aperiodic_tid += 1
        f.close()
        # arrange by phase time
        self.aperiodic_jobs = sorted(self.aperiodic_jobs, key= lambda x: x.phase_time)


    def simulate(self, save_path):
        
        clock = self.clock_start_time
        arrived_periodic_jobs = []
        arrived_aperiodic_jobs = []
        for periodic_job in self.periodic_jobs:
            if periodic_job.phase_time == 0:
                arrived_periodic_jobs.append(copy.deepcopy(periodic_job))
        # self.maxSimTime = 10
        while clock <= self.maxSimTime:
            # update current time 
            self.scheduler.update_clock(current_clock= clock)
            for periodic_job in self.periodic_jobs:
                period = periodic_job.period
                # if clock smaller than phase time, there is not job. 
                if clock < period:
                    continue
                if clock % period == 0:
                    arrived_periodic_jobs.append(copy.deepcopy(periodic_job))
            for aperiodic_job in self.aperiodic_jobs:
                phase_time = aperiodic_job.phase_time
                if clock == phase_time:
                    arrived_aperiodic_jobs.append(copy.deepcopy(aperiodic_job))
            self.scheduler.arriving_new_job(periodic_jobs= arrived_periodic_jobs, aperiodic_jobs= arrived_aperiodic_jobs)
            self.scheduler.work()
            
            # update status
            clock +=1
            arrived_periodic_jobs = []
            arrived_aperiodic_jobs = []
        self.scheduler.print_output()   
        self.scheduler.save(save_path= f"./hw2/testcase_res/{save_path}_res.txt") 



if __name__ == "__main__":

    schedulers = ["TBS", "CUS"]
    test_files = ["1", "2", "3"]
    for scheduler in schedulers:
        for test_file in test_files:
            simulator = simulation(
                periodic_file_path = f"./hw2/testcase/{test_file}/periodic.txt",
                aperiodic_file_path= f"./hw2/testcase/{test_file}/aperiodic.txt",
                scheduler= scheduler
            )
            simulator.simulate(save_path= f"{scheduler}_{test_file}")