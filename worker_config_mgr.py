# -*- coding: utf-8 -*-

import ConfigParser
import os

__author__ = 'duhyeong1.kim'



##########################################set config#######################################################
cfg = ConfigParser.RawConfigParser()
cfg.read(os.path.join(os.path.dirname("__file__"),'config.cfg'))
##########################################set config#######################################################

def get_config(option):
    return cfg.get('urqa',option)