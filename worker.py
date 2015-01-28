
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
import pika
import json
import base64
import logging
import os
from worker_config_mgr import get_config
from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import *
from sqlalchemy import desc
from worker_model import *;
from worker_util import *
import redis
import uuid
import jpype as mjpype
import subprocess

PROJECT_DIR = os.getcwd();

##########################################init logger#######################################################
LOG_DIR = "./worker_log"
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

log_file_path=os.path.join(LOG_DIR, str(os.getpid())+".log")
logging.basicConfig(filename = log_file_path , level=logging.INFO)
##########################################init logger#######################################################

##########################################init rabbitmq######################################################
print "start of pika init"
credentials = pika.PlainCredentials(get_config("pika_id"), get_config("pika_pwd"))
parameters  = pika.ConnectionParameters(host=get_config("pika_ip"),
                                        port=int(get_config("pika_port")),
                                        credentials=credentials)
connection  = pika.BlockingConnection(parameters)
channel     = connection.channel()

queue_name = get_config("queue_name")
exchange_name = get_config("exchange_name")
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange =exchange_name, queue = queue_name)
print "end of pika init"
##########################################init rabbitmq######################################################


##########################################init pidpath######################################################
#make file for identity my pid
pid_path = "/var/run/urqa-workers/"

#파일이 경로가존재하지 않으면 경로를 만든다.
if not os.path.exists(pid_path) :
    os.mkdir(pid_path)

#step 1 : get current screen name
m_argv = sys.argv
filename = None

if len(m_argv) == 1:
    filename = 'root'

else :
    filename=m_argv[1]

filename = filename + ".pid"

pid_file_path = pid_path + filename

#if file is already existed, remove this file
if os.path.exists(pid_file_path):
    os.remove(pid_file_path)

#filename을 지정해 파일 생성
pid_file=open(pid_file_path, "w+")

#create file
pid_file.write(str(os.getpid()))
pid_file.close()

##########################################init redis###################################################
redis_server = redis.Redis('localhost')
ex_stored_time = str(session.query(Appruncount2).order_by(desc(Appruncount2.idappruncount2)).first().datetime);
print "end of redis init"
##########################################init redis###################################################

##########################################init jvm###################################################
if not mjpype.isJVMStarted():
    mjpype.startJVM(get_config("jvm_path"), "-Djava.class.path=" + get_config("proguard_retrace_path"))
proguard_package=mjpype.JPackage("proguard.retrace")
retrace_class=proguard_package.ReTrace

print "end of jvm"
##########################################init jvm###################################################

print " [*] Waiting for messages. To exit press CTRL+C"

def callback(ch, method, properties,body):

    #해당 연산을 하면 python dictionary으로 만들어지게 된다.
    firstData = json.loads(body,encoding='utf-8')

    #tag정보와 body정보로 구분한다. tag정보는 데이터를 분류할 떄 사용한다.
    try:
        tag = firstData['tag']
        data_body = firstData['data']
        origin_time = firstData['date_time']
    except Exception as e:
        print "cannot parsing data from firstData"
        print e
        return

    if tag == 'connect':
        save_connection(data_body,origin_time)

    elif tag == 'receive_exception':
        save_exception(firstData,data_body,origin_time);

    elif tag == 'receive_native':
        save_native_exception(firstData,data_body,origin_time);


def save_connection(data_body,origin_time):
        #print "connect"
        #step1: apikey를  project찾기
        try:
            apikey = data_body['apikey']
            appversion = data_body['appversion']
        except Exception as e:
            print "cannot parsing data from data_body"
            print e
            return
        projectElement = session.query(Projects).filter_by(apikey=apikey).first()

        if projectElement == None:
            print "cannot find project using" + str(apikey)
            return

        cur_stored_time = str(get_translated_time2(origin_time));
        global ex_stored_time
        #print projectElement.name
        #step2: app version별 누적카운트 증가하기
        try:
            #step2 -1: 현재 시간과 이전 저장 시간을 비교한다.
            if(cur_stored_time != ex_stored_time):
                print type(redis_server.get("lock"))
                if(redis_server.get("lock") == None):
                    try :
                        redis_server.set("lock",1);
                        bulk_insert_query = "INSERT INTO appruncount2 VALUES"
                        mKeys = redis_server.keys();
                        for key in mKeys:
                            if key == 'lock':
                                continue
                            #if ex_stored_time in str(key):
                            if str(key).find(cur_stored_time) == -1:
                                splited_data = key.split("_")
                                q_pid = splited_data[0]
                                q_datetime = splited_data[1]
                                q_appversion = splited_data[2]
                                q_appruncount=redis_server.get(key)
                                redis_server.delete(key)
                                bulk_insert_query += " (NULL, {pid},'{datetime}','{appversion}',{appruncount}),".format(pid=q_pid,datetime=q_datetime,appversion=q_appversion,appruncount=q_appruncount)
                        bulk_insert_query=bulk_insert_query[0:len(bulk_insert_query)-1] + ";"
                        print bulk_insert_query
                        session.execute(bulk_insert_query)
                    finally:
                        redis_server.delete("lock");
        except Exception as e:
            print "watch err"
            print e

        #step2-3 현재 데이터를 redis에 저장한다.
        session_data = str(projectElement.pid) + "_" + cur_stored_time + "_" + str(appversion)
        ex_stored_time = cur_stored_time;
        redis_server.incr(session_data);





def save_exception(firstData, data_body, origin_time):
        logging.info("save exception")

        #step 1 : data가 유효한지 확인하기.
        jsonData=client_data_validate(data_body)

        #time1은 15분단위로 자른 시간을 의미한다.
        time1= get_translated_time1(origin_time);

        #step1: apikey를 이용하여 project찾기
        logging.info("step 1 : find project using apikey")
        try:
            apikey = jsonData['apikey']
            projectElement =  session.query(Projects).filter_by(apikey = apikey).first()
            if projectElement == None:
                raise Exception
            pid = projectElement.pid;
        #apikey가 없거나 해당 apieky가 유효하지 않을때 에러 발생시키고 리턴
        except Exception as e:
            print e
            print 'Invalid apikey'
            return

        #step2: errorname, errorclassname, linenum을 json에서 가져오기
        logging.info("step 2 : parse data from json")
        try:
            errorname = jsonData['errorname'].encode('utf-8')
            errorclassname = jsonData['errorclassname'].encode('utf-8')
            callstack = jsonData['callstack'].encode('utf-8')
            linenum = jsonData['linenum']
            appversion = jsonData['appversion']
            osversion=jsonData['osversion']
            devicename=jsonData['device']
            countryname=jsonData['country']
            activityname=jsonData['lastactivity']

        except Exception as e:
            print "cannot parsing data from jsonData"
            logging.error(str(e))
            return

        logging.info(firstData)

        map_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
        map_path = os.path.join(map_path,projectElement.apikey)
        map_path = os.path.join(map_path,appversion)

        #progurd가 적용된지 확인하는 부분!!!
        logging.info("step 2 - 0 : check this project is adapted using proguard")
        try:
            mapElement=session.query(Proguardmap).filter_by(pid = int(projectElement.pid), appversion = appversion).first()
            if mapElement == None:
                raise NoResultFound
            print "before adapting proguard"
            print "a"
            errorname, errorclassname, callstack = proguard_retrace_errors(retrace_class,errorname,errorclassname,linenum,callstack,map_path,mapElement.filename);
            print "b"
        except NoResultFound as e :
            print "no result found in proguard map"
            mapElement = None


        try:
            logging.info("step 2-1-1 save error")
            errorElement = session.query(Errors).filter_by(pid = int(projectElement.pid), errorclassname=str(errorclassname), errorname = str(errorname), linenum = str(linenum)).first()
            if errorElement == None:
                print "errorElement is None"
                raise NoResultFound
            #새로온 인스턴스 정보로 시간 갱신
            errorElement.callstack = callstack
            errorElement.lastdate = time1
            errorElement.numofinstances += 1
            errorElement.wifion += int(jsonData['wifion'])
            errorElement.gpson += int(jsonData['gpson'])
            errorElement.mobileon += int(jsonData['mobileon'])
            errorElement.totalmemusage += int(jsonData['appmemtotal'])
            session.add(errorElement)
            session.flush()
            logging.info("step 2-1-2 update appstatistics")
            iderror = errorElement.iderror
            query = '''UPDATE appstatistics SET count = count + 1 WHERE iderror = {iderror} and appversion = "{appversion}" and pid = {pid};'''.format(iderror=iderror, appversion=appversion, pid = pid);
            session.execute(query)

            logging.info("step 2-1-2 update osstatistics")
            query = '''UPDATE osstatistics SET count = count + 1 WHERE iderror = {iderror} and osversion = "{osversion}" and pid = {pid};'''.format(iderror=iderror, osversion=osversion, pid = pid);
            session.execute(query)

            logging.info("step 2-1-2 update devicestatistics")
            query = '''UPDATE devicestatistics SET count = count + 1 WHERE iderror= {iderror} and devicename = "{devicename}";'''.format(iderror=iderror, devicename=devicename);
            session.execute(query)

            logging.info("step 2-1-2 update countrystatistics")
            query = '''UPDATE countrystatistics SET count = count + 1 WHERE iderror = {iderror} and countryname = "{countryname}";'''.format(iderror=iderror, countryname=countryname);
            session.execute(query)

            logging.info("step 2-1-2 update activitystatistics")
            query = '''UPDATE activitystatistics SET count = count + 1 WHERE iderror = {iderror} and activityname = "{activityname}";'''.format(iderror=iderror, activityname=activityname);
            session.execute(query)
            logging.info("step 2-1 complete")

        except NoResultFound:
            autodetermine = 0

            logging.info("step 2-2 save error and update statistics")
            errorElement = Errors(
                pid = projectElement.pid,
                errorname = errorname,
                errorclassname = errorclassname,
                linenum = linenum,
                autodetermine = autodetermine,
                rank = int(jsonData['rank']), # Undesided = -1, unhandled = 0, critical = 1, major = 2, minor = 3, native = 4
                status = 0, # 0 = new, 1 = open, 2 = fixed, 3 = ignore
                createdate = time1,
                lastdate = time1,
                numofinstances = 1,
                callstack = callstack,
                wifion = jsonData['wifion'],
                gpson = jsonData['gpson'],
                mobileon = jsonData['mobileon'],
                totalmemusage = jsonData['appmemtotal'],
                errorweight = 10,
                recur = 0,
            )

            try:
                session.add(errorElement)
                session.flush()
                session.add(Appstatistics(iderror=int(errorElement.iderror),appversion=jsonData['appversion'],count=1, pid = pid))
                session.flush()
                session.add(Osstatistics(iderror=errorElement.iderror,osversion=jsonData['osversion'],count=1, pid = pid))
                session.flush()
                session.add(Devicestatistics(iderror=errorElement.iderror,devicename=jsonData['device'],count=1))
                session.flush()
                session.add(Countrystatistics(iderror=errorElement.iderror,countryname=jsonData['country'],count=1))
                session.flush()
                session.add(Activitystatistics(iderror=errorElement.iderror,activityname=jsonData['lastactivity'],count=1))
                session.flush()

            except Exception as e:
                print "add err"
                print e

        #step3: 테그 저장
        logging.info("step 3 : save tag")
        if jsonData['tag']:
            tagstr = jsonData['tag']
            # 단순 create 연산으로 바꿀것.
            tagElement, created = get_or_create(session,Tags, iderror=errorElement.iderror,pid=projectElement.pid,tag=tagstr)

        #step4: 인스턴스 생성하기
        logging.info("step 4 : create instance")
        instanceElement = Instances(
            pid = pid,
            iderror = errorElement.iderror,
            ins_count = errorElement.numofinstances,
            sdkversion = jsonData['sdkversion'],
            appversion = jsonData['appversion'],
            osversion = jsonData['osversion'],
            kernelversion = jsonData['kernelversion'],
            appmemmax = jsonData['appmemmax'],
            appmemfree = jsonData['appmemfree'],
            appmemtotal = jsonData['appmemtotal'],
            country = jsonData['country'],
            datetime = time1,
            locale = jsonData['locale'],
            mobileon = jsonData['mobileon'],
            gpson = jsonData['gpson'],
            wifion = jsonData['wifion'],
            device = jsonData['device'],
            rooted = jsonData['rooted'],
            scrheight = jsonData['scrheight'],
            scrwidth = jsonData['scrwidth'],
            scrorientation = jsonData['scrorientation'],
            sysmemlow = jsonData['sysmemlow'],
            log_path = '',
            batterylevel = jsonData['batterylevel'],
            availsdcard = jsonData['availsdcard'],
            xdpi = jsonData['xdpi'],
            ydpi = jsonData['ydpi'],
            lastactivity = jsonData['lastactivity'],
            callstack = callstack,
        )

        # primary key가 Auto-incrementing이기 때문에 save한 후 primary key를 읽을 수 있다.
        session.add(instanceElement)
        session.flush()

        #step 4-0 해당 인스턴스 아이디로 콘솔로그 저장
        logging.info("step 4 - 0 : save console log")
        if firstData.has_key("log"):
            log = firstData['log'].encode('utf-8');
            save_log(session,instanceElement.idinstance,log,time1);


        #step5: 이벤트패스 생성
        print "save event path"
        logging.info("step 5 : save event path")
        event_path = jsonData['eventpaths']
        save_event_pathes(session, retrace_class,event_path,instanceElement,errorElement,mapElement,map_path)

        logging.info("save exception is complete")

def save_native_exception(firstData, data_body, origin_time):
        logging.info("receive_native")
        jsonData = client_data_validate(data_body)
        #time1은 15분단위로 자른 시간을 의미
        time1=get_translated_time1(origin_time);
        #step1: apikey를 이용하여 project찾기
        logging.info("step 1: find project using apikey")
        #apikey가 validate한지 확인하기.
        try:
            apikey = jsonData['apikey']
            projectElement = session.query(Projects).filter_by(apikey=apikey).first();
            if projectElement == None:
                raise NoResultFound
            pid = projectElement.pid
        except NoResultFound:
            print 'Invalid apikey'
            return

        #step2: dummy errorElement생성
        #새로 들어온 에러라면 새로운 에러 생성
        logging.info("step 2: if this error is new, make new error instance")
        autodetermine = 0

        errorElement = Errors(
            pid = projectElement.pid,
            errorname = 'dummy',
            errorclassname = 'native',
            linenum = 0,
            autodetermine = autodetermine,
            rank = int(jsonData['rank']), # Undesided = -1, unhandled = 0, critical = 1, major = 2, minor = 3, native = 4
            status = 0, # 0 = new, 1 = open, 2 = ignore, 3 = renew
            createdate = time1,
            lastdate = time1,
            callstack = '',#jsonData['callstack'],
            wifion = jsonData['wifion'],
            gpson = jsonData['gpson'],
            mobileon = jsonData['mobileon'],
            numofinstances = 1,
            totalmemusage = jsonData['appmemtotal'],
            errorweight = 10,
            recur = 0,
        )
        session.add(errorElement)
        session.flush()

        #step3: 테그 저장
        logging.info("step 3 : save tag")
        tagstr = jsonData['tag']
        if tagstr:
            tagElement, created = get_or_create(session,Tags,id=errorElement.iderror, pid=projectElement.pid, tag=tagstr)

        #step4: 인스턴스
        logging.info("step 4 : make instance")
        instanceElement = Instances(
            pid = pid,
            iderror = errorElement.iderror,
            ins_count = errorElement.numofinstances,
            sdkversion = jsonData['sdkversion'],
            appversion = jsonData['appversion'],
            osversion = jsonData['osversion'],
            kernelversion = jsonData['kernelversion'],
            appmemmax = jsonData['appmemmax'],
            appmemfree = jsonData['appmemfree'],
            appmemtotal = jsonData['appmemtotal'],
            country = jsonData['country'],
            datetime = time1,
            locale = jsonData['locale'],
            mobileon = jsonData['mobileon'],
            gpson = jsonData['gpson'],
            wifion = jsonData['wifion'],
            device = jsonData['device'],
            rooted = jsonData['rooted'],
            scrheight = jsonData['scrheight'],
            scrwidth = jsonData['scrwidth'],
            scrorientation = jsonData['scrorientation'],
            sysmemlow = jsonData['sysmemlow'],
            log_path = '',
            batterylevel = jsonData['batterylevel'],
            availsdcard = jsonData['availsdcard'],
            xdpi = jsonData['xdpi'],
            ydpi = jsonData['ydpi'],
            lastactivity = jsonData['lastactivity']
        )
        # primary key가 Auto-incrementing이기 때문에 save한 후 primary key를 읽을 수 있다.
        session.add(instanceElement)
        session.flush()

        #step5: 이벤트패스 생성
        logging.info("step 5 : make event path")
        appversion = jsonData['appversion']

        map_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
        map_path = os.path.join(map_path,projectElement.apikey)
        map_path = os.path.join(map_path,appversion)

        try:
            #mapElement = Proguardmap.objects.get(pid=projectElement,appversion=appversion)
            mapElement = session.query(Proguardmap).filter_by(pid=projectElement.pid, appversion=appversion).first()
            if mapElement == None:
                raise NoResultFound
        except NoResultFound:
            mapElement = None
            print 'no proguard mapfile'

        #step5-0:이벤트 패스 실제로 만드는 부분
        logging.info("step 5 : make event path using save_event_pathes")
        print 'instanceElement.idinstance',instanceElement.idinstance
        eventpath = jsonData['eventpaths']
        save_event_pathes(session,retrace_class,eventpath,instanceElement,errorElement,mapElement,map_path)

        #step6 : 로그 정보 저장
        logging.info("step 6 : save log")
        if firstData.has_key("log"):
            log = firstData['log'].encode('utf-8');
            save_log(session,instanceElement.idinstance,log,time1);

        #step 7 :native dump data 저장 및 breakpad사용 데이터 분석
        #step 7 -1 : native dump 데이터 저장
        #what is dump?
        logging.info("step 7 - 1 : save natvie dump data")
        dump_path = os.path.join(PROJECT_DIR,os.path.join(get_config('dmp_pool_path'), '%s.dmp' % str(instanceElement.idinstance)))
        f = file(dump_path,'w')
        f.write(base64.b64decode(firstData['dump_data']))
        print "DUMP DATA ------>" + base64.b64decode(firstData['dump_data']);
        f.close()
        print 'log received : %s' % dump_path
        #step3: 저장한 로그파일을 db에 명시하기
        instanceElement.dump_path = dump_path
        session.add(instanceElement)
        session.flush()

        #step 7 -2 dmp 파일 분석
        #step4: dmp파일 분석(with nosym)
        logging.info("step 7 - 2 : analyze dump file")
        print "before no sym"
        arg = [os.path.join(PROJECT_DIR,get_config('minidump_stackwalk_path')) , dump_path]
        fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = fd_popen.communicate()
        print "communiction result " + str(stdout) + " " +str(stderr)
        print "after no sym"
        logging.info("result stdout : " + stdout)
        logging.info("result stderr : " + stderr)

        #step 7-3 : so library 추출
        logging.info("step 7 - 3 : extract so library")
        libs = []
        stderr_split = stderr.splitlines()
        for line in stderr_split:
            if line.find('Couldn\'t load symbols') == -1: #magic keyword
                continue
            lib = line[line.find('for: ')+5:].split('|')
            if lib[1] == '000000000000000000000000000000000' or lib[0] in Ignore_clib.list:
                continue
            #print lib[1] + ' ' + lib[0]
            libs.append(lib)

        #step 7-4 : DB저장하기
        logging.info("step 7 - 4: save dump file")
        for lib in libs:
            sofileElement, created = get_or_create2(session,Sofiles,defaults={'uploaded':'X'}, pid=projectElement.pid, appversion=instanceElement.appversion, versionkey=lib[1], filename=lib[0]);
            #필요없는로직
            if created:
                print 'new version key : ', lib[1], lib[0]
            else:
                print 'version key:', lib[1], lib[0], 'already exists'

        #step 7-5 : ErrorName, ErrorClassname, linenum 추출하기
        logging.info("step 7 - 5: extract errorname, errorclassname, linenum")
        cs_flag = 0
        errorname = ''
        errorclassname = ''
        linenum = ''
        stdout_split = stdout.splitlines()
        for line in stdout_split:
            if line.find('Crash reason:') != -1:
                errorname = line.split()[2]
            if cs_flag:
                if line.find('Thread') != -1 or errorclassname:
                    break
                #errorclassname 찾기
                for lib in libs:
                    flag = line.find(lib[0])
                    if flag == -1:
                        continue
                    separator = line.find(' + ')
                    if separator != -1:
                        errorclassname = line[flag:separator]
                        linenum = line[separator+3:]
                    else:
                        errorclassname = line[flag:]
                        linenum = 0
                    break
            if line.find('(crashed)') != -1:
                cs_flag = 1

        #dmp파일 분석(with sym)
        logging.info("step 7 - 6 : analyze dump file")
        sym_pool_path = os.path.join(PROJECT_DIR,os.path.join(get_config('sym_pool_path'),str(projectElement.apikey)))
        sym_pool_path = os.path.join(sym_pool_path, instanceElement.appversion)
        arg = [os.path.join(PROJECT_DIR,get_config('minidump_stackwalk_path')) , dump_path, sym_pool_path]
        fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = fd_popen.communicate()

        cs_count = 0
        callstack = ''
        stdout_split = stdout.splitlines()
        for line in stdout_split:
            if line.find('(crashed)') != -1:
                callstack = line
                cs_count = cs_count + 1
            elif cs_count:
                if line.find('Thread') != -1 or cs_count > 40:
                    break;
                callstack += '\n'
                callstack += line
                cs_count = cs_count + 1
        logging.info("step 8 : save error")
        try:
            #저에러랑 이에러랑 같은건데 실제로는 저걸로 검색이 안되서 내가 고민하는 거임
            #errorElement_exist = Errors.objects.get(pid=projectElement, errorname=errorname, errorclassname=errorclassname, linenum=linenum)
            errorElement_exist = session.query(Errors).filter_by(pid=projectElement.pid, errorname=errorname, errorclassname=errorclassname, linenum=linenum).first()
            if errorElement_exist == None:
                raise NoResultFound
            logging.info("step 8- 1 : when error already exist")
            errorElement_exist.lastdate = errorElement.lastdate
            errorElement_exist.numofinstances += 1
            errorElement_exist.wifion += errorElement.wifion
            errorElement_exist.gpson += errorElement.gpson
            errorElement_exist.mobileon += errorElement.mobileon
            errorElement_exist.totalmemusage += errorElement.totalmemusage
            session.add(errorElement_exist)
            session.flush();

            instanceElement.iderror = errorElement_exist.iderror
            iderror = instanceElement.iderror

            session.add(instanceElement)
            session.flush()
            #change it to update query
            logging.info("step 8-2 : update statistics")
            logging.info("step 8-2-1 : update appstatistics")
            query = '''UPDATE appstatistics SET count = count + 1 WHERE iderror = {iderror} and appversion = "{appversion}" and pid = {pid};'''.format(iderror=iderror, appversion=appversion, pid = pid);
            session.execute(query)
            logging.info("step 8-2-1 : update osstatistics")
            query = '''UPDATE osstatistics SET count = count + 1 WHERE iderror = {iderror} and osversion = "{osversion}" and pid = {pid};'''.format(iderror=iderror, osversion=instanceElement.osversion, pid = pid);
            logging.info("executed query : " + query);
            session.execute(query)
            logging.info("step 8-2-1 : update devicestatistics")
            logging.info("hello")
            query = '''UPDATE devicestatistics SET count = count + 1 WHERE iderror= {iderror} and devicename = "{devicename}";'''.format(iderror=iderror, devicename=instanceElement.device);
            logging.info(query);
            session.execute(query)
            logging.info("step 8-2-1 : update countrystatistics")
            query = '''UPDATE countrystatistics SET count = count + 1 WHERE iderror = {iderror} and countryname = "{countryname}";'''.format(iderror=iderror, countryname=instanceElement.country);
            session.execute(query)
            logging.info("step 8-2-1 : update activitystatistics")
            query = '''UPDATE activitystatistics SET count = count + 1 WHERE iderror = {iderror} and activityname = "{activityname}";'''.format(iderror=iderror, activityname=instanceElement.lastactivity);
            session.execute(query)
            print "before deleting"
            logging.info("step 8-3 : delete errorElement");
            session.delete(errorElement)
            session.flush()
            print 'native error %s:%s already exist' % (errorname, errorclassname)
        except NoResultFound:
            logging.info("step 8- 1 : when error does not exist")
            errorElement.errorname = errorname
            errorElement.errorclassname = errorclassname
            errorElement.callstack = callstack
            errorElement.linenum = linenum
            session.add(errorElement)
            session.flush();

            session.add(Appstatistics(iderror=errorElement.iderror,appversion=instanceElement.appversion,count=1, pid = pid))
            session.flush()
            session.add(Osstatistics(iderror=errorElement.iderror,osversion=instanceElement.osversion,count=1, pid = pid))
            session.flush()
            session.add(Devicestatistics(iderror=errorElement.iderror,devicename=instanceElement.device,count=1))
            session.flush()
            session.add(Countrystatistics(iderror=errorElement.iderror,countryname=instanceElement.country,count=1))
            session.flush()
            session.add(Activitystatistics(iderror=errorElement.iderror,activityname=instanceElement.lastactivity,count=1))
            session.flush()
        logging.info("complete receive_native");
        print "complete receive_native"



def finalize():
    mjpype.shutdownJVM()
    connection.close()
    sys.exit(1)

if __name__ == '__main__':
    try :
        try:
            channel.basic_consume(callback, queue=queue_name, no_ack=True)
            channel.start_consuming()
        except Exception as e:
            print e
            logging.error(e)
            channel.stop_consuming()
    finally :
        finalize()













