'''datetimeの利用(dt)
'''
from system.loggerSetting import getMyLogger
from system.paramSetting  import getParam, setParam, hasParam, loadParams
from system.shutdownSetting import register_shutdown_hook
from system.decoratorSetting import instrumented, retryCounter

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