import subprocess

def run_script(script_path):
    return subprocess.Popen(['python', script_path])

if __name__ == "__main__":
    tsunami_process = run_script('simulation-scenarios/tsunami.py')
    uav4res_process = run_script('simulation-scenarios/UAV4Res.py')
    random_uav_process = run_script('simulation-scenarios/randomUAV.py')
    tsunami_process.wait()
    uav4res_process.wait()
    random_uav_process.wait()