'''datetimeの利用(dt)
'''
from lib.loggerSetting import getMyLogger
from lib.paramSetting  import getParam, setParam, hasParam, loadParams
from lib.shutdownSetting import register_shutdown_hook
from lib.decoratorSetting import instrumented, retryCounter

# 日付評価用の関数
from datetime import datetime, date, time, timedelta, timezone

logger = getMyLogger(__name__)

@instrumented()
def evalAction(command):
    """Python式を評価し結果をreturnパラメータに格納
    
    Args:
        command (str): 評価するPython式
    
    Warning:
        eval使用のため任意コード実行のリスクあり
    """
    
    print("DEBUG:", command)
    result = str(eval(command))
    logger.info(f'returnパラメータに{result}を格納しました')
    return result
    


action_list = {
    'eval' : evalAction,
}