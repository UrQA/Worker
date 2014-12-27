# -*- coding: utf-8 -*-

import logging
import os

__author__ = 'duhyeong1.kim'



##########################################init logger#######################################################
LOG_DIR = "./worker_log"
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

log_file_path=os.path.join(LOG_DIR, str(os.getpid())+".log")
logging.basicConfig(filename = log_file_path , level=logging.INFO)
##########################################init logger#######################################################