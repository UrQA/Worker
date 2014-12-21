# -*- coding: utf-8 -*-
import datetime
import pytz
import os
import ConfigParser
import sys
import uuid
from worker_model import Eventpaths
import time

__author__ = 'dookim'

class Ignore_clib:
    list = [
        'libWVStreamControlAPI_L1',
        'libwebviewchromium',
        'libLLVM.so',
        'libdvm.so',
        'libc.so',
        'libcutils.so',
        'app_process',
        'libandroid_runtime.so',
        'libutils.so',
        'libbinder.so',
        'libjavacore.so',
        'librs_jni.so',
        'linker',
    ]


def get_translated_time(origin_time):
    return origin_time[:10]

def get_translated_time1(origin_time):
    return origin_time[:19]

def get_translated_time2(origin_time):
    now_minute = int(origin_time[14:16])

    if 0 <= now_minute and now_minute < 15:
         now_minute_str = '00'
    elif 15 <= now_minute and  now_minute < 30:
         now_minute_str = '15'
    elif 30 <= now_minute and now_minute < 45:
         now_minute_str = '30'
    elif 45 <= now_minute and now_minute < 60:
         now_minute_str = '45'

    translated_minute = origin_time[:14]+now_minute_str + ":00"
    return translated_minute



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


def get_or_create2(session, model, defaults=None, **kwargs):

    query = session.query(model).filter_by(**kwargs)
    instance = query.first()

    if instance :
        print "this is read operation"
        return instance, False
    else:
        print "this is write operation"
        if not defaults == None :
            kwargs.update(defaults)
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
        return instance, True

def make_random_file_with_content(content,path) :
    temp_file_name = str(uuid.uuid1());
    temp_path_and_name = os.path.join(path,temp_file_name + ".txt");
    fp = open(temp_path_and_name , 'wb');
    fp.write(content);
    fp.close();
    return temp_path_and_name;

def proguard_retrace_errors(retrace_class, errorname, errorclassname, linenum, callstack, map_path, map_filename) :
    start_time = time.time();
    query = 'at\t'+errorname+'\t(:%s)' % linenum + "\n";
    query += 'at\t'+errorclassname+'\t(:%s)' % linenum + "\n";
    query += callstack + "\n";
    print "before callstack"
    print callstack

    map_path_and_name=os.path.join(map_path,map_filename);
    print map_path_and_name

    temp_result = retrace_class.getRetracedResult(query, map_path_and_name)
    print "temp result"
    print temp_result
    splited_temp_result = temp_result.split("\n");

    errorname = splited_temp_result[0]
    errorclassname = splited_temp_result[1]
    callstack = ""
    for i in range(2, len(splited_temp_result)):
        callstack += splited_temp_result[i] + "\n"

    print "errorname"
    print errorname
    print "errorclassname"
    print errorclassname
    print "callstack"
    print callstack
    end_time = time.time()
    print "processed time : " + str(end_time - start_time)
    return errorname, errorclassname, callstack;

def save_event_pathes(session,retrace_class, event_path, instanceElement, errorElement ,mapElement, map_path):
    if len(event_path) == 0:
        print "event path is 0"
        return;
    depth = 10
    if mapElement == None:
        for event in reversed(event_path):
            classname = event['classname'];
            methodname = event['methodname']
            linenum = event['linenum']
            if not 'label' in event:    #event path에 label적용, 기존버전과 호환성을 확보하기위해 'label'초기화를 해줌 client ver 0.91 ->
                event['label'] = ""
            label = event['label'];
            #label이 300byte가 넘어갈경우 잘라줌
            if(len(label) > 300) :
                label = label[0:300];

            eventpathInstance=Eventpaths(
                idinstance = instanceElement.idinstance,
                iderror = errorElement.iderror,
                ins_count = errorElement.numofinstances,
                datetime = naive2aware(event['datetime']),
                classname = classname,
                methodname = methodname,
                linenum = linenum,
                label = label,
                depth = depth
            )
            session.add(eventpathInstance)
            session.flush()
            depth -= -1;
    else :
        #step 1 : make proguard query
        query = get_event_path_queries(event_path);
        map_path_and_name=os.path.join(map_path,mapElement.filename);
        print "query"
        print query
        temp_result = retrace_class.getRetracedResult(query, map_path_and_name)
        print "temp result"
        print temp_result
        result_list = temp_result.split('\n')
        print "result_list"
        print result_list
        i = 0
        print "len of event path : " +str(len(event_path))
        for event in reversed(event_path):
            temp_str = result_list[i]
            print "class and method"
            print temp_str
            flag = temp_str.rfind('.')
            classname = temp_str[0:flag]
            methodname =  temp_str[flag+1:]
            linenum = event['linenum']
            if not 'label' in event:    #event path에 label적용, 기존버전과 호환성을 확보하기위해 'label'초기화를 해줌 client ver 0.91 ->
                event['label'] = ""
            eventpathInstance=Eventpaths(
                idinstance = instanceElement.idinstance,
                iderror = errorElement.iderror,
                ins_count = errorElement.numofinstances,
                datetime = naive2aware(event['datetime']),
                classname = classname,
                methodname = methodname,
                linenum = linenum,
                label = event['label'],
                depth = depth
            )
            session.add(eventpathInstance)
            session.flush()
            depth -= -1;
            i += 1;

def get_event_path_queries(event_path):
    proguard_query = ""
    for event in reversed(event_path):
        temp_str = event['classname'] + '.' + event['methodname']
        linenum = event['linenum'];
        proguard_query += 'at\t'+temp_str+'\t(:%s)' % linenum + "\n";
    return proguard_query;

def proguard_retrace_event_pathes(retrace_class, query, map_path, map_filename):
    map_path_and_name=os.path.join(map_path,map_filename);
    print map_path_and_name
    temp_result = retrace_class.getRetracedResult(query, map_path_and_name)
    result_list = temp_result.split('\n')
    return result_list;

def proguard_retrace_callstack(retrace_class, content, map_path, map_filename) :
    print "before callstack"
    print content
    temp_path_and_name = make_random_file_with_content(content,map_path);
    print temp_path_and_name
    map_path_and_name=os.path.join(map_path,map_filename);
    print map_path_and_name
    arg = ['-verbose',map_path_and_name,temp_path_and_name]
    result=retrace_class.getRetracedResult(arg)
    print "after callstack"
    print result
    os.remove(temp_path_and_name)
    return result
'''
def proguard_retrace_oneline(retrace_class, content, linenum, map_path, map_filename) :
    proguard_query = 'at\t'+content+'\t(:%s)' % linenum;
    print proguard_query
    temp_path_and_name = make_random_file_with_content(proguard_query,map_path);
    print temp_path_and_name
    map_path_and_name=os.path.join(map_path,map_filename);
    print map_path_and_name
    arg = ['-verbose',map_path_and_name,temp_path_and_name]
    temp_result=retrace_class.getRetracedResult(arg)
    result=temp_result.split('\t')[1];
    os.remove(temp_path_and_name)
    return result
'''
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





