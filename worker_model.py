# -*- coding: utf-8 -*-

from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import *
from sqlalchemy import desc
from worker_config_mgr import get_config;

__author__ = 'duhyeong1.kim'

print "start alchemy init"
try :
    Base = declarative_base()
    print "mysql://" + get_config("mysql_accnt") + ":" + get_config("mysql_pwd") + "@" + get_config("mysql_ip") + ":" + get_config("mysql_port") +"/" +get_config("mysql_db_name") +"?charset=utf8";
    engine= create_engine("mysql://" + get_config("mysql_accnt") + ":" + get_config("mysql_pwd") + "@" + get_config("mysql_ip") + ":" + get_config("mysql_port") +"/" +get_config("mysql_db_name") +"?charset=utf8",encoding='utf-8',echo=False)
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

class Appruncount2(Base):
    __table__ = Table('appruncount2', metadata, autoload=True)

class Sofiles(Base):
    __table__ = Table('sofiles', metadata, autoload=True)
print "end of alchemy init"
