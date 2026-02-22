from logging import getLogger
import logging
import logging.handlers

from system.paramSetting import getParam

logger = None

class AbbreviatedFormatter(logging.Formatter):
    # ログレベル名を固定長の短縮名に変換
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

    fh_path     = getParam('fh.path', '.\log\trace.log')
    max_bytes    = getParam('fh.max_bytes', 1048576)
    backup_count = getParam('fh.backup_count', 3)
    encoding    = getParam('fh.encoding', 'utf-8')

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



# # queuハンドラ版（ファイル出力にはいいかもしれない）
# from logging.handlers import QueueHandler, QueueListener
# from queue import Queue

# listener = None  # モジュールグローバル or 戻り値で返す

# def setLogger():
#     global logger, listener
#     root_logger_name = getParam('root_logger_name', 'CommandRPA')
#     logger = getLogger(root_logger_name)
#     logger.setLevel(logging.DEBUG)

#     if logger.handlers:
#         logger.handlers.clear()

#     # --- ログフォーマット関連設定 ---
#     fh_path     = getParam('fh.path', '.\log\trace.log')
#     max_bytes    = getParam('fh.max_bytes', 1048576)
#     backup_count = getParam('fh.backup_count', 3)
#     encoding    = getParam('fh.encoding', 'utf-8')
#     fh_level    = getattr(logging, getParam('fh.level', 'DEBUG').upper())
#     ch_level    = getattr(logging, getParam('ch.level', 'INFO').upper())
#     fh_format   = getParam('fh.format')
#     ch_format   = getParam('ch.format')
#     fh_datefmt  = getParam('fh.datefmt')
#     ch_datefmt  = getParam('ch.datefmt')

#     # --- 実際の出力先ハンドラ（Listener用） ---
#     file_handler = logging.handlers.RotatingFileHandler(
#         fh_path, maxBytes=max_bytes, backupCount=backup_count, encoding=encoding)
#     file_handler.setLevel(fh_level)
#     file_handler.setFormatter(AbbreviatedFormatter(fmt=fh_format, datefmt=fh_datefmt))

#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(ch_level)
#     console_handler.setFormatter(AbbreviatedFormatter(fmt=ch_format, datefmt=ch_datefmt))

#     # --- QueueHandlerのセットアップ ---
#     log_queue = Queue(-1)
#     queue_handler = QueueHandler(log_queue)
#     logger.addHandler(queue_handler)  # logger には QueueHandler だけ追加

#     # --- QueueListenerの起動 ---
#     listener = QueueListener(log_queue, file_handler, console_handler, respect_handler_level=True)
#     listener.start()

#     return logger
