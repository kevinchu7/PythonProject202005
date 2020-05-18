# -*- coding: utf-8 -*-
# 日志
import os, sys
import logging.handlers

from conf import settings


class Logger:
    logger = logging.getLogger()
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    logfile = os.path.join(settings.LOG_PATH, sys.argv[0].split('/')[-1].split('.')[0]) + '.log'
    fh = logging.handlers.RotatingFileHandler(filename=logfile, maxBytes=settings.LOG_SIZE,
                                              backupCount=settings.LOG_NUM, encoding='utf-8')
    ch = logging.StreamHandler()

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.setLevel(level=logging.INFO)

    logger.addHandler(fh)
    logger.addHandler(ch)

    @classmethod
    def info(cls, msg):
        cls.logger.info(msg)

    @classmethod
    def warning(cls, msg):
        cls.logger.warning(msg)

    @classmethod
    def error(cls, msg):
        cls.logger.error(msg)

