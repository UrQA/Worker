import os
import time
from URQAProcess import URQAProcess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEBase
from email.mime.text import MIMEText
from email import Encoders
from email import Utils
from email.header import Header
import subprocess

# pegasus command 
# apache2 pid file path "/var/run/apache2.pid" or command: "service apache2 status"

# PIDS_DIR_PATH change
# PIDS_DIR_PATH = os.path.abspath(os.path.dirname(__file__)) + '/pid'
PIDS_DIR_PATH = '/var/run/urqa-workers/'
print PIDS_DIR_PATH
NOTIFY_RETRY_COUNT = 10
WAIT_TIME = 10

# process state
activate = True
# retry count
retry = 0
cur_pid_list = []
cur_pid_map_list = []
process_killed_flag = False
# get currnet all pid list about worker
def read_cur_worker_pid():
    #step 1 : get pid list
    #proc = subprocess.Popen(["ps -ef|grep python|grep worker|awk '{print $2}'"], stdout=subprocess.PIPE, shell=True)
    command = "ps -ef|grep python|grep worker|awk {'print $2 " " $9'}"
    proc = subprocess.Popen([command],stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    temp_list=out.split("\n")
    print temp_list
    #step 2 : get even pid list
    j = 1
    for temp_pid in temp_list :
        #print i
        if(j%2 == 0 and temp_pid.__contains__("worker")):
            print temp_pid
            index = temp_pid.index("w")
            pid = temp_pid[:index]
            executed_file = temp_pid[index:len(temp_pid)]
            cur_pid_list.append(pid)
            print "pid       :     asdfasfsadfdsafadsf" + pid
            cur_pid_map_list.append({"executed_file":executed_file,"pid":pid})
            print cur_pid_map_list
        j += 1

    for temp in cur_pid_list:
        print temp

# do not use anymore
def read_file(file_name):

    path_and_name = PIDS_DIR_PATH + str(file_name)
    print path_and_name

    with open(path_and_name) as pid_file:
        pid = pid_file.readline()
        pid = pid.rstrip()
        data = {'fullpath': path_and_name, 'pid': pid, 'script_name': file_name}
        return data


def read_pids():
    # step 0 :init
    global ps_data
    temp_pid_files = os.listdir(PIDS_DIR_PATH)
    pid_files = []

    # step 1 : if pid file doesn't belong to current pid list, it should be deleted.
    for pid_file in temp_pid_files:

        #step 1 :get current files pid name
        print "pid file : " + pid_file
        screen_name = pid_file.split(".")[0]
        print screen_name
        pid = None
        path_and_name = PIDS_DIR_PATH + pid_file
        with open(path_and_name) as pid_file:
            pid = pid_file.readline()
            pid = pid.rstrip()

        #step 2 : if pid which don't run now, remove from list and file system
        if not pid in cur_pid_list:
            os.remove(path_and_name)
            print "if not"
            print pid_file
        else :
            index = cur_pid_list.index(pid)
            executed_file = cur_pid_map_list[index]['executed_file']
            print "executed file :    " + executed_file
            pid_files.append({'fullpath': path_and_name, 'pid': pid, 'script_name': str(pid_file),"screen_name":screen_name,"executed_file":executed_file})
    ps_data = pid_files



def prepare():
    global processes
    processes = []
    #print "ps data : " + ps_data[0]
    for data in ps_data:
         
        process = URQAProcess(data)
        processes.append(process)

def send_mail(from_user, pwd, to_user, cc_users, subject, text, attach):
        COMMASPACE = ", "
        msg = MIMEMultipart("alternative")
        #msg =  MIMEMultipart()
        msg["From"] = from_user
        msg["To"]   = to_user
        msg["Cc"] = COMMASPACE.join(cc_users)
        msg["Subject"] = Header(s=subject, charset="utf-8")
        msg["Date"] = Utils.formatdate(localtime = 1)
        msg.attach(MIMEText(text, "html", _charset="utf-8"))

        if (attach != None):
                part = MIMEBase("application", "octet-stream")
                part.set_payload(open(attach, "rb").read())
                Encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment; filename=\"%s\"" % os.path.basename(attach))
                msg.attach(part)

        smtp_server  = "smtp.gmail.com"
        port         = 587

        smtp = smtplib.SMTP(smtp_server, port)
        smtp.starttls()
        smtp.login(from_user, pwd)
        print "gmail login OK!"
        smtp.sendmail(from_user, cc_users, msg.as_string())
        print "mail Send OK!"
        smtp.close()

def init():
    print "A~~~~~ZZ"
    process_killed_flag = False
    read_cur_worker_pid()
    read_pids()
    prepare()


read_cur_worker_pid()
read_pids()
prepare()

while True:
    for process in processes:
        print process
        if process.is_alive():
            print "alive"
        else:
            if(process.screen_name == "test") :
                processes.remove(process)
                send_mail("urqanoti@gmail.com","@urqa@stanly","doo871128@gmail.com",["doo871128@gmail.com"],"[ERROR Report] test Worker dead!!","test Worker dead!!",None)
            else :
                process.retry_with_screen()
                send_mail("urqanoti@gmail.com","@urqa@stanly","doo871128@gmail.com",["doo871128@gmail.com"],"[ERROR Report] release Worker dead!!","release Worker dead!!",None)
    time.sleep(WAIT_TIME)
