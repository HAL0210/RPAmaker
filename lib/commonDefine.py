"""他のファイルで共通で利用する定義を集約する。

このファイルは "窓口" として複数モジュールの名前を再エクスポートします。
Pylance (pyright) の未使用 import 警告はこのファイル単体で無視する設定にしています。
"""

# pyright: reportUnusedImport=false

# libモジュール定義（再エクスポートの窓口）
from lib.loggerSetting import getMyLogger
from lib.paramSetting  import getParam, setParam, hasParam, loadParams
from lib.shutdownSetting import register_shutdown_hook
from lib.decoratorSetting import instrumented, retryCounter
from lib.customFunction import (
	patternMatchSplit,
	sepSplit,
	tableDisplay,
	false_list,
	toBool,
	encode_url_component,
	decode_url_component,
)

# よく使うライブラリ
import time
import sys
import re
import os


# 明示的に公開する名前を定義することで再エクスポートの意図を明確にする
__all__ = [
	'getMyLogger',
	'getParam', 'setParam', 'hasParam', 'loadParams',
	'register_shutdown_hook',
	'instrumented', 'retryCounter',
	'patternMatchSplit', 'sepSplit', 'tableDisplay', 'false_list', 'toBool',
	'encode_url_component', 'decode_url_component',
    'time', 'sys', 're', 'os',
]

