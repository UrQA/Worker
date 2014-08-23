import os
import subprocess
import psutil
import time
class URQAProcess:
    def __init__(self, ps_data=None):
        """URQAProcess!!!"""
        if ps_data is None:
            print "PID filename must be not null"
            raise
        self.fullpath = ps_data['fullpath']
        self.pid = int(ps_data['pid'])
        self.script_name = os.getcwd() + '/run-' + ps_data['script_name'].split('.')[0]
        self.screen_name = ps_data['screen_name']
        self.executed_file = ps_data['executed_file']
        print "executed file in process : " +self.executed_file
	#print "screen name in process: " +ps_data['screen_name']
        #print self.script_name
        #print "hello  ps data : " + ps_data['script_name']
        self.retried = False
        self.alive = False

        self.get_process()

    def read_pid(self):
        with open(self.fullpath) as pid_file:
            print "new pid is "+str(self.pid)
            self.pid = int(pid_file.readline().rstrip())

    def get_process(self):
        self.process = psutil.Process(self.pid)
        if self.process.is_running():
            self.alive = True
            self.retried = False
        else:
            self.alive = False

    def is_alive(self):
        if self.process is None:
            return False
        return self.process.is_running()

    def retry(self):
        # get_process_info()
        if self.retried:
            self.read_pid()
            self.get_process()
            return
        print self.script_name
        subprocess.call(["/bin/sh", self.script_name, "start"])
        self.retried = True
    def retry_with_screen(self):
        #step 1 : make new process
        command = '''screen -S {} -X stuff "sudo python {} {}
	"
	'''.format(self.screen_name,self.executed_file,self.screen_name)
        proc = subprocess.Popen([command],stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        #step 1-0 : wait for this process is alive
        time.sleep(2)
        #step 2 : replace pid
        self.read_pid()
        self.get_process()
        return 
        #screen -S "monitor" -X stuff "sudo python /home/urqa/worker/urqa_worker/worker_monitor/mon.py
        #"
    def __repr__(self):
        return "URQAProcess: " + self.fullpath + '(' + str(self.pid) + ')'

    def __str__(self):
        return "URQAProcess: " + self.fullpath + '(' + str(self.pid) + ')'


