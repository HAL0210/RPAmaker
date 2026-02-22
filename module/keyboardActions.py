'''キーボード操作(k)
'''
from pynput.keyboard import Controller, Key
from system.commonDefine import *

keyboard = Controller()
loadParams('mod/keyboard.yaml')
logger = getMyLogger(__name__)

key_map = {
    # 修飾キー
    'ctrl'      : Key.ctrl,
    'shift'     : Key.shift,
    'alt'       : Key.alt,
    'cmd'       : Key.cmd,
    'win'       : Key.cmd,
    'windows'   : Key.cmd,

    # 入力・編集キー
    'enter'     : Key.enter,
    'tab'       : Key.tab,
    'space'     : Key.space,
    'backspace' : Key.backspace,
    'delete'    : Key.delete,
    'insert'    : Key.insert,

    # ナビゲーションキー
    'up'        : Key.up,
    'down'      : Key.down,
    'left'      : Key.left,
    'right'     : Key.right,
    'home'      : Key.home,
    'end'       : Key.end,
    'page_up'   : Key.page_up,
    'page_down' : Key.page_down,

    # ロックキー
    'caps_lock'     : Key.caps_lock,
    'num_lock'      : Key.num_lock,
    'scroll_lock'   : Key.scroll_lock,

    # ファンクションキー
    'f1'        : Key.f1,
    'f2'        : Key.f2,
    'f3'        : Key.f3,
    'f4'        : Key.f4,
    'f5'        : Key.f5,
    'f6'        : Key.f6,
    'f7'        : Key.f7,
    'f8'        : Key.f8,
    'f9'        : Key.f9,
    'f10'       : Key.f10,
    'f11'       : Key.f11,
    'f12'       : Key.f12,
    'f13'       : Key.f13,
    'f14'       : Key.f14,
    'f15'       : Key.f15,
    'f16'       : Key.f16,
    'f17'       : Key.f17,
    'f18'       : Key.f18,
    'f19'       : Key.f19,
    'f20'       : Key.f20,

    # システム・その他キー
    'esc'           : Key.esc,
    'pause'         : Key.pause,
    'print_screen'  : Key.print_screen,
    'menu'          : Key.menu,
}

def keySelect(key):
    key = key.lower()
    if key in key_map:
        return key_map[key]
    elif len(key) == 1:
        return key


@instrumented()
def typeAction(text):
    """テキストをキーボード入力する

    Args:
        text (str): 入力する文字列

    Notes:
        - TYPE_INTERVALが設定されている場合、各文字の間にウェイトを入れて入力します
    """
    type_interval = getParam('TYPE_INTERVAL', 0)
    if type_interval == 0:
        keyboard.type(text)
    else:
        for char in text:
            keyboard.type(char)
            time.sleep(type_interval)


@instrumented()
def keyAction(keys_str):
    """複数キーの組み合わせ（ショートカットキーなど）を押して離す

    Args:
        keys_str (str): '+'区切りで表現されたキー列（例："ctrl+shift+s"）

    Notes:
        - 左から順にpress、最後のキーをtap、押した順とは逆順でrelease
    """     
    keys = sepSplit(keys_str, sep='+', split=0)
    for key in keys[:-1]:
        pressAction(key)
    tapAction(keys[-1])
    for key in reversed(keys[:-1]):
        releaseAction(key)


@instrumented()
def pressAction(key):
    """
    指定したキーを押す（押しっぱなしにする）

    Args:
        key (str): 押すキーを指定
    
    Note:
        releaseされていないとアプリ終了後も押した状態になるので注意
        その場合はもう一度押せば直る想定
    """
    keyboard.press(keySelect(key))


@instrumented()
def releaseAction(key):
    """
    指定したキーを離す（リリースする）

    Args:
        key (str): 離すキーを指定
    """
    keyboard.release(keySelect(key))


@instrumented()
def tapAction(key):
    """
    指定したキーを1回タップ（押してすぐ離す）

    Args:
        key (str): タップするキーを指定
    """
    keyboard.tap(keySelect(key))


@instrumented()
def listAction():
    '''
    利用可能なキーの一覧を出力する

    Args:
        なし
    '''
    tableDisplay(key_map)


action_list = {
    'type' : typeAction,
    'key'  : keyAction,
    'press': pressAction,
    'release': releaseAction,
    'tap'    : tapAction,
    'list' : listAction
}