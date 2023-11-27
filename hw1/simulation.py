from shedule_tool.task import task
import timer
from shedule_tool.RM import RM 
from shedule_tool.EDF import EDF 
from shedule_tool.strictSLT import strictSLT
import os

class simulation:

    def __init__(self, file_path, schedule_tool):
        self.__load_file(file_path= file_path)
        self.clock_start_time = 0
        self.schedule_tool = schedule_tool
        self.schedule_tool.reset()

    def __load_file(self, file_path):
        
        tid = 1
        self.all_tasks = []
        with open(file_path, "r") as f: 
            for raw_task in f.readlines():
                phase_time, period, relative_deadline, execution_time = raw_task.split(",") 
                ea_task = task(phase_time= phase_time, period= period.strip(), 
                    relative_deadline= relative_deadline.strip(), 
                    execution_time= execution_time.strip(), tid= tid)
                self.all_tasks.append(ea_task)
                tid += 1
        for tt in self.all_tasks:
            print(tt.phase_time, tt.period, tt.relative_deadline, tt.execution_time)
        self.__get_lcd_task_period()
        self.__get_max_phase_time()
        self.all_tasks_phase_time = [ea_task.phase_time for ea_task in self.all_tasks]
        self.all_tasks_period = [ea_task.period for ea_task in self.all_tasks]

    def check_schedulability(self):
        return self.schedule_tool.schedulability_test(all_tasks = self.all_tasks)
    
    def __gcd(self, a, b):
        if a < b:
            a , b = b, a
        return b if a % b == 0 else self.__gcd(b, a % b)

    def __get_lcd_task_period(self):
        
        self.lcd_period = self.all_tasks[0].period
        mutli_period = self.lcd_period
        for idx in range(1, len(self.all_tasks)):
            mutli_period *= self.all_tasks[idx].period
            gcd_period = self.__gcd(self.lcd_period, self.all_tasks[idx].period)
            self.lcd_period = mutli_period / gcd_period

        # print("period: ", self.lcd_period)
    def __get_max_phase_time(self):

        self.max_phase_time = -1
        for ea_task in self.all_tasks:
            self.max_phase_time = max(self.max_phase_time, ea_task.phase_time)
        
        return self.max_phase_time

    def simulate(self):
        
        clock = self.clock_start_time 
        while clock < self.lcd_period + self.max_phase_time:
            # update current_time to schedule tool
            self.schedule_tool.update_time(current_time = clock)
            for idx in range(len(self.all_tasks)):
                # if clock smaller than phase time, there is not job. 
                if clock < self.all_tasks_phase_time[idx]:
                    continue
                if (clock - self.all_tasks_phase_time[idx]) % self.all_tasks_period[idx] == 0:
                    self.schedule_tool.get_new_task(task = self.all_tasks[idx])
            self.schedule_tool.check_miss_deadline_job()
            self.schedule_tool.check_preemptive_job()
            self.schedule_tool.check_execution_phase()

            clock += 1

    def print_record(self, save_path):
        self.schedule_tool.print_record(save_path = save_path)


if __name__ == "__main__":
    case = "democase"
    file_path = f"./hw1/{case}"
    run = [[ RM(), "RM"], [EDF(), "EDF"], [strictSLT(), "strictSLT"]]
    for file in os.listdir(file_path):
        # file = "test6.txt"
        for schedule, file_name in run:
            # schedule = EDF()
            simulator = simulation(file_path= file_path + "/"  + file, schedule_tool= schedule)
            if file_name != "strictSLT":
                simulator.check_schedulability()
            simulator.simulate()
            simulator.print_record(save_path= f"./hw1/{case}_res/{file_name}/{file}")
            
    