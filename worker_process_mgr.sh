#!/bin/bash
# step 1 :kill all process
ps -ef | grep python | grep worker |  awk '{ print $2 }' | sudo xargs kill -9
# step 2 : run all process with screen
for i in 2 3
do
   #echo "Welcome $i times"
   #screen -X -S "worker$i" quit
   if ! screen -list |grep -q "worker$i"; then 
	screen -S "worker$i" -d -m   	
   fi
   sleep 0.1
   screen -S "worker$i" -X stuff "sudo python worker.py worker$i 
"
   sleep 0.1
done

# kill monitor : kill monitor
ps -ef|grep python | grep mon | awk '{print $2}' | sudo xargs kill -9

sleep 0.1
#if none, make monitor screen
if ! screen -list |grep -q "monitor1"; then
        screen -S "monitor1" -d -m
fi
sleep 0.1
screen -S "monitor1" -X stuff "sudo python /home/urqa/worker/urqa_worker/worker_monitor/mon.py
"

