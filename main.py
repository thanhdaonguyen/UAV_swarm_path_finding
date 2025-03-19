import subprocess
from input import *

def run_script(script_path):
    return subprocess.Popen(['python', script_path])

if __name__ == "__main__":
    f = open("output.txt", 'a')
    f.write(f"map type: {maptype}, num of uavs: {num_of_uavs} \n")
    
    #tsunami_process = run_script('simulation-scenarios/tsunami.py')
    uav4res_process = run_script('simulation-scenarios/UAV4Res.py')
    tsunami_without_priority = run_script('simulation-scenarios/Tsunami_without_priority.py')
    #random_uav_process = run_script('simulation-scenarios/randomUAV.py')
    random_uav_cluster_process = run_script('simulation-scenarios/randomUAVCluster.py')
    #tsunami_process.wait()
    uav4res_process.wait()
    #random_uav_process.wait()
    tsunami_without_priority.wait()
    random_uav_cluster_process.wait()