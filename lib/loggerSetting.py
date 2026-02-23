from logging import getLogger
import logging
import logging.handlers
import os

from lib.paramSetting import getParam

logger = None

class AbbreviatedFormatter(logging.Formatter):
    LEVEL_ABBR = {
        'DEBUG':    '[DEBUG]',
        'INFO':     '[INFO] ',
        'WARNING':  '[WARN] ',
        'ERROR':    '[ERROR]',
        'CRITICAL': '[FATAL]',
    }
    
    def format(self, record):
        record.levelname = self.LEVEL_ABBR.get(record.levelname, record.levelname)
        return super().format(record)

def setLogger():
    global logger
    root_logger_name = getParam('root_logger_name', 'CommandRPA')
    logger = getLogger(root_logger_name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    fh_path     = getParam('fh.path', '.\\log\\trace.log')
    max_bytes    = getParam('fh.max_bytes', 1048576)
    backup_count = getParam('fh.backup_count', 3)
    encoding    = getParam('fh.encoding', 'utf-8')

    # ログファイルのディレクトリが存在しない場合は作成する
    fh_dir = os.path.dirname(fh_path)
    if fh_dir and not os.path.exists(fh_dir):
        os.makedirs(fh_dir, exist_ok=True)

    fh_level = getattr(logging, getParam('fh.level', 'DEBUG').upper())
    ch_level = getattr(logging, getParam('ch.level', 'INFO').upper())

    fh_format = getParam('fh.format')
    ch_format = getParam('ch.format')

    fh_datefmt = getParam('fh.datefmt')
    ch_datefmt = getParam('ch.datefmt')

    fh = logging.handlers.RotatingFileHandler(
        fh_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding=encoding
        )
    fh.setLevel(fh_level)
    fh.setFormatter(AbbreviatedFormatter(fmt=fh_format, datefmt=fh_datefmt))

    ch = logging.StreamHandler()
    ch.setLevel(ch_level)
    ch.setFormatter(AbbreviatedFormatter(fmt=ch_format, datefmt=ch_datefmt))

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

def getMyLogger(name):
    return getLogger(f'{getParam("root_logger_name")}.{name}')
