'''
他のファイルで共通で利用する定義を集約する。
'''

# systemモジュール定義
from system.loggerSetting import getMyLogger
from system.paramSetting  import getParam, setParam, hasParam, loadParams
from system.shutdownSetting import register_shutdown_hook
from system.decoratorSetting import instrumented, retryCounter
from system.customException import *
from system.customFunction import *

# よく使うライブラリ
import time
import sys
import re
import os

