
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
import pika
import json
import MySQLdb as db
import pytz

import subprocess
import datetime
import datetime
import logging
import time
import datetime
from dateutil import tz
import os
import string
import ConfigParser
import httplib, urllib
import signal
from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import *


from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import ClauseElement


#set logger
LOG_DIR = "./worker_log"
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
logging.basicConfig(filename = os.path.join(LOG_DIR, str(os.getpid())+".log") , level=logging.INFO)
#rabbit mq서버에 접속, exchanger생성하고  exchanger와 queue끼리 바인딩 시킴.
credentials = pika.PlainCredentials('urqa', 'urqa')
parameters  = pika.ConnectionParameters(host='127.0.0.1',
                                        port=5672,
                                        credentials=credentials)

connection  = pika.BlockingConnection(parameters)
channel     = connection.channel()

channel.queue_declare(queue='urqa.queue', durable=True)
channel.queue_bind(exchange ='urqa.exchange', queue = 'urqa.queue')

#PROJECT_DIR = get_config('project_dir')
PROJECT_DIR = "/home/urqa/URQA-Server/soma3"
#PROJECT_DIR = "/home/urqa/urqa/release/" 

cfg = ConfigParser.RawConfigParser()
cfg.read(os.path.join(os.path.dirname(__file__),'config.cfg'))
#print 'config.py'

#make file for identity my pid
pid_path = "/var/run/urqa-workers/"
#파일이 경로가존재하지 않으면 경로를 만든다.
if not os.path.exists(pid_path) :
    os.mkdir(pid_path)

#filename지정
filelist = os.listdir(pid_path)
worker_index = len(filelist) + 1
filename = "worker" + str(worker_index) + ".pid"

path_and_name = pid_path + filename

#filename을 지정해 파일 생성
pid_file=open(path_and_name, "w+")
err_log_file= open(pid_path + str(os.getpid()) + ".txt","w+");

#create file
pid_file.write(str(os.getpid()))
pid_file.close()

def get_config(option):
    return cfg.get('urqa',option)

#'latin-1' codec can't encode characters in position 0-2: ordinal not in range(256)

#SQL ALCHEMY를 사용한 DB CONNECTION을 맺는 부분
#Create and engine and get the metadata
try :
    Base = declarative_base()
    engine= create_engine("mysql://root:@stanly@urqa@127.0.0.1:3306/urqa?charset=utf8",encoding='utf-8',echo=False)
    #engine= create_engine("mysql://root:@stanly@urqa/urqa?charset=utf8",encoding='utf-8',echo=False)
    #engine= create_engine("mysql://root:@stanly@urqa@125.209.196.85/urqa",encoding='utf-8',echo=True)
    metadata = MetaData(bind=engine)
    session = create_session(bind=engine)
except Exception as e:
    print e
    print "cannot bind DB using Alchemy"


#SCHEMA BIND시키는 부분
class Instances(Base):
    __table__ = Table('instances', metadata, autoload=True)

class Projects(Base):
    __table__ = Table('projects', metadata, autoload=True)

class Proguardmap(Base):
    __table__ = Table('proguardmap', metadata, autoload=True)

class Errors(Base):
    __table__ = Table('errors', metadata, autoload=True)

class Appstatistics(Base):
    __table__ = Table('appstatistics', metadata, autoload=True)

class Osstatistics(Base):
    __table__ = Table('osstatistics', metadata, autoload=True)

class Devicestatistics(Base):
    __table__ = Table('devicestatistics', metadata, autoload=True)

class Countrystatistics(Base):
    __table__ = Table('countrystatistics', metadata, autoload=True)

class Activitystatistics(Base):
    __table__ = Table('activitystatistics', metadata, autoload=True)

class Tags(Base):
    __table__ = Table('tags', metadata, autoload=True)

class Eventpaths(Base):
    __table__ = Table('eventpaths', metadata, autoload=True)

class Appruncount(Base):
    __table__ = Table('appruncount', metadata, autoload=True)






print " [*] Waiting for messages. To exit press CTRL+C"
def callback(ch, method, properties,body):
    #print " [x] Received %r\n\n" % (body,)

    #해당 연산을 하면 python dictionary으로 만들어지게 된다.
    firstData = json.loads(body,encoding='utf-8')

    # 데이터 형식
    #var data = { 'tag':'connect', 'data': req.body };

    #tag정보와 body정보로 구분한다. tag정보는 데이터를 분류할 떄 사용한다.
    try:
        tag = firstData['tag']
        data_body = firstData['data']
        date_time = firstData['date_time']
    except Exception as e:
        print "cannot parsing data from firstData"
        print e
        return
    #idinstance = firstData['idinstance']

    if tag == 'connect':
	print "connect"

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
        #print projectElement.name
        #step2: app version별 누적카운트 증가하기
        try:
            #print "today   ==========  " + today
            appruncountElement, created = get_or_create2(session,Appruncount, defaults={'runcount':1}, pid=int(projectElement.pid),appversion=str(appversion),date=str(date_time) )
        except Exception as e:
            print "get_or_create_err"
            print e
            return

        if created == False:
            try:
                appruncountElement.runcount += 1
                session.add(appruncountElement)
                session.flush()
            except Exception as e:
                print "appruncount err"
                print e
                return


    elif tag == 'receive_exception':
        logging.info(body)

        #step 1 : idinstance에 해당하는 인스턴스 구하기
        #idinstance=firstData["idinstance"]
        #jsonData
        jsonData = data_body
        jsonData=client_data_validate(jsonData)

        #step1: apikey를 이용하여 project찾기
        #apikey가 validate한지 확인하기.
        try:
            apikey = jsonData['apikey']
            #projectElement = Projects.objects.get(apikey=apikey)
            projectElement =  session.query(Projects).filter_by(apikey = apikey).first()
            if projectElement == None:
                raise Exception
        #apikey가 없거나 해당 apieky가 유효하지 않을때 에러 발생시키고 리턴
        except Exception as e:
            print e
            print 'Invalid apikey'
            return
        logging.info("step 1 complete")



        print >> sys.stderr, 'receive_exception requested',apikey

        #step2: errorname, errorclassname, linenum을 이용하여 동일한 에러가 있는지 찾기
        try:
            errorname = jsonData['errorname']
            errorclassname = jsonData['errorclassname']
            linenum = jsonData['linenum']
        except Exception as e:
            print "cannot parsing data from jsonData"
            logging.error(str(e))
            return

        print >> sys.stderr, 'appver:', jsonData['appversion'], 'osver:', jsonData['osversion']
        print >> sys.stderr, '%s %s %s' % (errorname,errorclassname,linenum)
        logging.info("step 2 complete")

        print firstData
        logging.info(firstData)

        #step2-0: Proguard 적용 확인
        try :
            appversion = jsonData['appversion']
        except Exception as e:
            print "appversion parsing err"
            return

        #map_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
        #map_path = '/home/urqa/urqa/release/mappool'
        map_path = os.path.join(PROJECT_DIR,get_config('proguard_map_path'))
        map_path = os.path.join(map_path,projectElement.apikey)
        map_path = os.path.join(map_path,appversion)

        print map_path
        logging.info("step 2-0 complete")
        try:
            mapElement=session.query(Proguardmap).filter_by(pid = int(projectElement.pid), appversion = appversion).first()
            if mapElement == None:
                raise NoResultFound
            print "a"
            print str(errorname) + " " + str(linenum) + " " + str(mapElement)
            errorname = proguard_retrace_oneline(errorname,linenum,map_path,mapElement)
            errorname = errorname.decode("unicode_escape")
            print "B"
            errorclassname = proguard_retrace_oneline(errorclassname,linenum,map_path,mapElement)
            print "c"
            callstack = proguard_retrace_callstack(jsonData['callstack'],map_path,mapElement)
            print "d"

        except NoResultFound as e :
            print "no result found in proguard map"
            mapElement = None
            callstack = jsonData['callstack']
            print 'no proguard mapfile'


        logging.info("step 2-1 complete")
        print "f"

        try:
            print "g"

            errorElement = session.query(Errors).filter_by(pid = int(projectElement.pid), errorclassname=str(errorclassname), errorname = str(errorname), linenum = str(linenum)).first()
            #errorElement = session.query(Errors).filter_by(pid = 142, errorclassname='android.view.ViewRootImpl', errorname = 'android.view.WindowManager$BadTokenException: Unable to add window -- token android.os.BinderProxy@42b44538 is not valid; is your activity running?', linenum = '727').first()
            if errorElement == None:
                print "errorElement is None"
                raise NoResultFound
            #새로온 인스턴스 정보로 시간 갱신
            #errorElement.lastdate = naive2aware(jsonData['datetime'])
            errorElement.callstack = callstack
            errorElement.lastdate = date_time    #getUTCawaredatetime1()
            errorElement.numofinstances += 1
            #errorElement.totalmemusage += jsonData['appmemtotal']
            errorElement.wifion += int(jsonData['wifion'])
            errorElement.gpson += int(jsonData['gpson'])
            errorElement.mobileon += int(jsonData['mobileon'])
            errorElement.totalmemusage += int(jsonData['appmemtotal'])
            session.add(errorElement)
            session.flush()

            e, created = get_or_create2(session, Appstatistics, defaults={'count':1},iderror=int(errorElement.iderror),appversion=str(jsonData['appversion']))
            if not created:
                e.count += 1
                session.add(e)
                session.flush()

            e, created = get_or_create2(session, Osstatistics, defaults={'count':1},iderror=int(errorElement.iderror),osversion=str(jsonData['osversion']))
            if not created:
                e.count += 1
                session.add(e)
                session.flush()

            e, created = get_or_create2(session, Devicestatistics, defaults={'count':1}, iderror=int(errorElement.iderror),devicename=str(jsonData['device']))
            if not created:
                e.count += 1
                session.add(e)
                session.flush()

            e, created = get_or_create2(session, Countrystatistics, defaults={'count':1}, iderror=int(errorElement.iderror),countryname=str(jsonData['country']))
            if not created:
                e.count += 1
                session.add(e)
                session.flush()

            e, created = get_or_create2(session, Activitystatistics, defaults={'count':1},iderror=int(errorElement.iderror),activityname=str(jsonData['lastactivity']))
            if not created:
                e.count += 1
                session.add(e)
                session.flush()

            logging.info("step 2-2 complete")


            #에러 스코어 계산 에러스코어 삭제
            #calc_errorScore(errorElement)

        except NoResultFound:

            #새로 들어온 에러라면 새로운 에러 생성
            #if int(jsonData['rank']) == -1:
            #    autodetermine = 1 #True
            #else:
            #    autodetermine = 0 #False
            autodetermine = 0

            errorElement = Errors(
                pid = projectElement.pid,
                errorname = errorname,
                errorclassname = errorclassname,
                linenum = linenum,
                autodetermine = autodetermine,
                rank = int(jsonData['rank']), # Undesided = -1, unhandled = 0, critical = 1, major = 2, minor = 3, native = 4
                status = 0, # 0 = new, 1 = open, 2 = fixed, 3 = ignore
                createdate = date_time # getUTCawaredatetime1(),
                lastdate = date_time   #getUTCawaredatetime1(),
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
                session.add(Appstatistics(iderror=int(errorElement.iderror),appversion=jsonData['appversion'],count=1))
                session.flush()
                session.add(Osstatistics(iderror=errorElement.iderror,osversion=jsonData['osversion'],count=1))
                session.flush()
                session.add(Devicestatistics(iderror=errorElement.iderror,devicename=jsonData['device'],count=1))
                session.flush()
                session.add(Countrystatistics(iderror=errorElement.iderror,countryname=jsonData['country'],count=1))
                session.flush()
                session.add(Activitystatistics(iderror=errorElement.iderror,activityname=jsonData['lastactivity'],count=1))
                #error score 계산 에러스코어 삭제
                #calc_errorScore(errorElement)
                session.flush()

            except Exception as e:
                print "add err"
                print e



        logging.info("step 2-3 complete")

        #step3: 테그 저장
        if jsonData['tag']:
            tagstr = jsonData['tag']
            tagElement, created = get_or_create(session,Tags, iderror=errorElement.iderror,pid=projectElement.pid,tag=tagstr)


        logging.info("step 3 complete")

        #step4: 인스턴스 생성하기
        instanceElement = Instances(

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
            datetime = date_time #getUTCawaredatetime1(),
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

        logging.info("step 4 complete")

        #step 4-0 해당 인스턴스 아이디로 콘솔로그 저장
        if firstData.has_key("log"):
            log_path = os.path.join(PROJECT_DIR,os.path.join(get_config('log_pool_path'), '%s.txt' % str(instanceElement.idinstance)))
            instanceElement.log_path = log_path
            session.add(instanceElement)
            session.flush()

            print log_path

            f = file(log_path,'w')
            f.write(firstData['log'].encode('utf-8'))
            f.close()

        logging.info("step 4-0 complete")

        #step5: 이벤트패스 생성
        #print 'here! ' + instanceElement.idinstance
        #instanceElement.update()
        print 'instanceElement.idinstance',instanceElement.idinstance

        eventpath = jsonData['eventpaths']

        depth = 10
        for event in reversed(eventpath):
            temp_str = event['classname'] + '.' + event['methodname']
            temp_str = proguard_retrace_oneline(temp_str,event['linenum'],map_path,mapElement)
            flag = temp_str.rfind('.')
            classname = temp_str[0:flag]
            methodname =  temp_str[flag+1:]
            if not 'label' in event:    #event path에 label적용, 기존버전과 호환성을 확보하기위해 'label'초기화를 해줌 client ver 0.91 ->
                event['label'] = ""
            event_path=Eventpaths(
                idinstance = instanceElement.idinstance,
                iderror = errorElement.iderror,
                ins_count = errorElement.numofinstances,
                datetime = naive2aware(event['datetime']),
                classname = classname,
                methodname = methodname,
                linenum = event['linenum'],
                label = event['label'],
                depth = depth
            )
            session.add(event_path)
            session.flush()
            depth -= 1
        logging.info("step 5 complete")

def getUTCawaredatetime():
    now = datetime.datetime.utcnow()
    time_str = '%04d-%02d-%02d %02d:%02d:%02d'  % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    naivetime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    time_str = str(naivetime.replace(tzinfo=pytz.utc))
    #return time_str[:10]
    return time_str[:10]

def getUTCawaredatetime1():
    now = datetime.datetime.utcnow()
    time_str = '%04d-%02d-%02d %02d:%02d:%02d'  % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    naivetime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    time_str = str(naivetime.replace(tzinfo=pytz.utc))
    #return time_str[:10]
    print time_str[:19]
    return time_str[:19]

def naive2aware(time_str):
    naivetime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return naivetime.replace(tzinfo=pytz.utc)


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
        return instance, True
'''
def get_or_create1(session, model, defaults=None, **kwargs):
    try:
        query = session.query(model).filter_by(**kwargs)

        instance = query.first()

        if instance:
            print "get data in get_or_create1" + str(instance)
            return instance, False
        else:
            try:

                params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
                if not defaults == None:
                    params.update(defaults)

                instance = model(**params)
                session.add(instance)
                session.flush()
                print "create in get_or_create1" +str(instance)
                return instance, True
            except Exception as e:
                print e
                print "IntegrityError raise"
                print "IntegrityError raise"
                session.rollback()
                instance = query.one()
                return instance, False
    except Exception as e:
        print e
        raise e

'''

def get_or_create2(session, model, defaults=None, **kwargs):

    query = session.query(model).filter_by(**kwargs)

    instance = query.first()

    if instance:
        return instance, False
    else:
        print "create in get_or_create1"
        if not defaults == None:
            kwargs.update(defaults)
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
        print "create success" +str(instance)
        return instance, True



def proguard_retrace_oneline(string,linenum,map_path,mapElement):
    if mapElement == None:
        return string
    for i in range(1,100):
        temp_path = os.path.join(map_path,'temp'+str(i)+'.txt')
        if not os.path.isfile(temp_path):
            break
    fp = open(temp_path , 'wb')
    fp.write('at\t'+string+'\t(:%s)' % linenum)
    fp.close()

    arg = ['java','-jar',os.path.join(PROJECT_DIR,get_config('proguard_retrace_path')),'-verbose',os.path.join(map_path,mapElement.filename),temp_path]
    #print arg
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()
    stdout_split = stdout.split('\t')
    string = stdout_split[1]

    os.remove(temp_path)
    return string


def proguard_retrace_callstack(string,map_path,mapElement):
    if mapElement == None:
        return string
    for i in range(1,100):
        temp_path = os.path.join(map_path,'temp'+str(i)+'.txt')
        if not os.path.isfile(temp_path):
            break
    fp = open(temp_path , 'wb')
    fp.write(string)
    fp.close()

    arg = ['java','-jar',os.path.join(PROJECT_DIR,get_config('proguard_retrace_path')),'-verbose',os.path.join(map_path,mapElement.filename),temp_path]
    #print arg
    fd_popen = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = fd_popen.communicate()
    string = stdout

    os.remove(temp_path)
    return string


def client_data_validate(jsonData):
    oriData = jsonData.copy();
    errorFlag = 0
    if not 'apikey' in jsonData:
        jsonData['apikey'] = 'unknown'
        errorFlag = 1
    if not 'errorname' in jsonData:
        jsonData['errorname'] = 'unknown'
        errorFlag = 1
    if len(jsonData['errorname']) >= 499:
        jsonData['errorname'] = jsonData['errorname'][0:499]
        errorFlag = 1
    if not 'errorclassname' in jsonData:
        jsonData['errorclassname'] = 'unknown'
        errorFlag = 1
    if len(jsonData['errorclassname']) >= 299:
        jsonData['errorclassname'] = jsonData['errorclassname'][0:299]
        errorFlag = 1
    if not 'linenum' in jsonData:
        jsonData['linenum'] = 'unknown'
        errorFlag = 1
    if not 'callstack' in jsonData:
        jsonData['callstack'] = 'unknown'
        errorFlag = 1
    if not 'wifion' in jsonData:
        jsonData['wifion'] = 0
        errorFlag = 1
    if not 'gpson' in jsonData:
        jsonData['gpson'] = 0
        errorFlag = 1
    if not 'mobileon' in jsonData:
        jsonData['mobileon'] = 0
        errorFlag = 1
    if not 'appversion' in jsonData:
        jsonData['appversion'] = 'unknown'
        errorFlag = 1
    if not 'osversion' in jsonData:
        jsonData['osversion'] = 'unknown'
        errorFlag = 1
    if not 'device' in jsonData:
        jsonData['device'] = 'unknown'
        errorFlag = 1
    if not 'country' in jsonData:
        jsonData['country'] = 'unknown'
        errorFlag = 1
    if not 'lastactivity' in jsonData:
        jsonData['lastactivity'] = 'unknown'
        errorFlag = 1
    if not 'rank' in jsonData:
        jsonData['rank'] = RANK.Critical
        errorFlag = 1
    if int(jsonData['rank']) < 0 or int(jsonData['rank']) > 4:
        jsonData['rank'] = RANK.Critical
        errorFlag = 1
    if not 'sdkversion' in jsonData:
        jsonData['sdkversion'] = 'unknown'
        errorFlag = 1
    if not 'kernelversion' in jsonData:
        jsonData['kernelversion'] = 'unknown'
        errorFlag = 1
    if not 'appmemmax' in jsonData:
        jsonData['appmemmax'] = 'unknown'
        errorFlag = 1
    if not 'appmemfree' in jsonData:
        jsonData['appmemfree'] = 'unknown'
        errorFlag = 1
    if not 'appmemtotal' in jsonData:
        jsonData['appmemtotal'] = 'unknown'
        errorFlag = 1
    if not 'locale' in jsonData:
        jsonData['locale'] = 'unknown'
        errorFlag = 1
    if not 'rooted' in jsonData:
        jsonData['rooted'] = 0
        errorFlag = 1
    if not 'scrheight' in jsonData:
        jsonData['scrheight'] = 0
        errorFlag = 1
    if not 'scrwidth' in jsonData:
        jsonData['scrwidth'] = 0
        errorFlag = 1
    if not 'scrorientation' in jsonData:
        jsonData['scrorientation'] = 0
        errorFlag = 1
    if not 'sysmemlow' in jsonData:
        jsonData['sysmemlow'] = 'unknown'
        errorFlag = 1
    if not 'batterylevel' in jsonData:
        jsonData['batterylevel'] = 0
        errorFlag = 1
    if not 'availsdcard' in jsonData:
        jsonData['availsdcard'] = 0
        errorFlag = 1
    if not 'xdpi' in jsonData:
        jsonData['xdpi'] = 0
        errorFlag = 1
    if not 'ydpi' in jsonData:
        jsonData['ydpi'] = 0
        errorFlag = 1
    if not 'eventpaths' in jsonData:
        jsonData['eventpaths'] = 'unknown'
        errorFlag = 1

    if errorFlag == 1:
        print >> sys.stderr, 'exception Data Error: ', oriData
        print >> sys.stderr, 'Revise JSON Data    : ', jsonData

    return jsonData


class RANK:
    toString = ['Unhandle','Native','Critical','Major','Minor']
    Suspense = -1
    Unhandle = 0
    Native   = 1
    Critical = 2
    Major    = 3
    Minor    = 4
    rankcolor = ['gray','purple','red','blue','green']
    rankcolorbit = ["#de6363", "#9d61dd", "#dca763", "#5a9ccc", "#72c380" ]

def redirect_post_msg(body,tag, url) :
    print "redirect post msg method"
    headers = {"Content-type": "application/x-www-form-urlencoded",
           "Accept": "text/plain"}
    params = json.dumps(body)
    conn = httplib.HTTPConnection("127.0.0.1:9001")
    #requets url을 넣을것.
    #urqa/client/send/exception/dump/(?P<idinstance>\d+
    #정규 표현식 문제
    conn.request("POST", url, params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()


if __name__ == '__main__':

    try:
        channel.basic_consume(callback, queue="urqa.queue", no_ack=True)
        channel.start_consuming()
    except (KeyboardInterrupt):#, SystemExit):
        print 'KeyboardInterrupt Program Exit....\n'
        os.remove(path_and_name)
    except Exception as e:
        print e
        os.remove(path_and_name)
        err_log_file.write(e.message);
        err_log_file.close()
        sys.exit(1)

	channel.stop_consuming()
    connection.close()
    sys.exit(1)









