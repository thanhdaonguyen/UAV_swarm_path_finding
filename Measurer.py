import time

class Measurer:
    def __init__(self):
        self.time = 0
        self.cost = 0
        self.initial_time = 0
        # data: [{time: amount of data}]
        self.recent_data = 0
        self.data = [{0: 0}] 
    
    def set_initial_time(self):
        self.initial_time = time.time()
    
    def get_time(self):
        self.time = time.time() - self.initial_time

    def add_cost(self, priority):
        self.cost += (time.time() - self.initial_time) * priority

    def get_data(self, data):
        self.recent_data += data
        self.data.append({time.time() - self.initial_time: self.recent_data}) 

    def print(self):
        print(f"time = {self.time}, cost = {self.cost}, data = \n {self.data}")