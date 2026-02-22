'''デスクトップアプリのUI操作(u)
'''
from pywinauto import Application, Desktop
from pywinauto.timings import Timings
from pywinauto.keyboard import send_keys
from pywinauto.findwindows import ElementNotFoundError, ElementAmbiguousError
from pynput import mouse, keyboard
import traceback
import threading
from system.paramSetting import *
from pywinauto.application import Application, AppStartError
from pywinauto.findwindows import ElementNotFoundError

from system.commonDefine import *

# exe化で必要
import comtypes.stream

loadParams('mod/ui.yaml')
logger = getMyLogger(__name__)

app = None

@instrumented()
def runAction(app_key_or_path=None):
    """UI要素を操作するアプリケーションを起動し、接続する関数

    アプリケーションのパスを直接指定するか、設定ファイルからエイリアス（キー）を使って取得し、
    `uia` バックエンドで起動・接続します。
    引数が省略された場合は対話形式で入力を求めます。

    Args:
        app_key_or_path (:obj:`str`, optional): アプリケーションの実行ファイルパスまたは設定されたキー名。
            - キー名の場合、設定ファイル(app_path)から対応する実行パスを取得します。
            - 直接ファイルパスを指定することも可能です。

    Returns:
        Application: 起動・接続したアプリケーションオブジェクト。
        
    Raises:
        AppStartError: アプリケーションの起動に失敗した場合。
        ElementNotFoundError: アプリケーションのUI要素に接続できなかった場合。
        Exception: その他の予期しないエラーが発生した場合。

    Examples:
        アプリ名（キー）を指定して起動：
        >>> runAction('notepad')
        パラメータ'app_path'から取得したパスで起動される

        直接パスを指定して起動：
        >>> runAction('C:\\\\Program Files\\\\MyApp\\\\myapp.exe')

        引数を省略して起動（対話入力）：
        >>> runAction()
        console: 実行するアプリ >> 起動したいアプリを入力する

    Note:
        - アプリケーションには `pywinauto.Application(backend='uia')` を使用します。
        - ダブルクォーテーションで囲まれたパスは自動で除去されます。
    """
    global app
    
    # 引数がない場合はアプリを対話形式で入力させる
    if not app_key_or_path:
        app_key_or_path = input('実行するアプリ >> ')
    
    # app_pathに登録済みのアプリの場合、パラメータからpath取得
    if hasParam(f'app_path.{app_key_or_path}'):
        app_path = getParam(f'app_path.{app_key_or_path}')
    else:
        app_path = app_key_or_path 
    
    # ダブルクォーテーション囲みの場合は除去する
    if app_path.startswith('"') and app_path.endswith('"'):
        app_path = app_path[1:-1]
    
    try:
        # アプリ実行
        app = Application(backend='uia')
        app.start(app_path)
        app.connect(path=app_path)
        return app
    except AppStartError as e:
        logger.error(f"アプリケーションの起動に失敗しました")
        raise
    except ElementNotFoundError as e:
        logger.error(f"アプリケーションに接続できませんでした")
        raise
    except Exception as e:
        logger.critical("想定外の例外が発生しました")
        raise


@instrumented()
def treeAction(app_key_or_path=None):
    """アプリケーションウィンドウのUIツリーを表示する関数

    指定されたアプリケーションを起動または再接続し、そのウィンドウ内に存在するUI要素の階層構造（コントロールツリー）を標準出力に表示します。
    UI要素のデバッグや自動化対象の特定に有用です。

    Args:
        app_key_or_path (:obj:`str`, optional): アプリケーションの実行ファイルパスまたは設定キー。
            - 指定された場合：新たにアプリを起動し接続します。（参考：ui.run）
            - 指定されない場合：既に接続済みの `app` オブジェクトを使用します。

    Returns:
        None: 標準出力にUIツリーを表示するだけで、値は返しません。

    Raises:
        ui.run(runAction)に依ります

    Examples:

        既存のアプリに接続しUIツリーを表示：
        >>> treeAction()

        アプリパスを指定してUIツリーを表示：
        >>> treeAction('notepad')

    Note:
        - UI要素の詳細情報は `pywinauto` の `print_control_identifiers()` によって出力されます。
    """
    global app
    if not app or app_key_or_path:
        app = runAction(app_key_or_path)
    # ツリー表示 
    app.window().print_control_identifiers()


@instrumented()
def inspectorAction(app_key_or_path=None):
    inspectAction(app_key_or_path, once=False)


@instrumented()
def inspectAction(app_key_or_path=None, once=True):
    global app
    if app_key_or_path:
        app = runAction(app_key_or_path)

    if app:
        target_pid = app.process  # ターゲットアプリのプロセスIDを取得
    exit_flag = threading.Event()  # 終了フラグ

    def on_click(x, y, button, pressed):
        if pressed:
            try:
                element = Desktop(backend='uia').from_point(x, y)
                window = element.top_level_parent()

                window_name   = window.window_text()
                pid           = window.process_id()
                window_class  = window.element_info.class_name
                automation_id = element.element_info.automation_id
                class_name    = element.friendly_class_name()
                name          = element.element_info.name
                text          = element.window_text()

                print("\n=== クリックされた要素 ===")
                print(f"ウィンドウ名: {window_name}")
                print(f"プロセスID: {pid}")
                print(f"クラス名: {window_class}")
                print("-"*30)
                print(f"位置: ({x}, {y})")
                print(f"Automation ID: {automation_id}")
                print(f"クラス名: {class_name}")
                print(f"名前: {name}")
                if hasattr(element, 'window_text'):
                    print(f"テキスト: {text}")
                if app:
                    if pid == target_pid:
                        print("-"*30)
                        query = ';'.join(filter(lambda x: x not in (None, ''), [
                            automation_id, class_name, name, text
                        ]))
                        print(f'query = {query}')
                        try:
                            elems = find_element(query, getAll=True)
                            index = elems.index(element)
                            print(f"query検索結果: {elems}")
                            print(f"query検索index: {index}")
                        except:
                            print('queryの再検索に失敗')
                print("="*30)

                if once:
                    exit_flag.set()

            except Exception as e:
                print(f"\n[エラー発生]\n{traceback.format_exc()}")
                raise

    def on_press(key):
        try:
            if key == keyboard.Key.esc:
                print("\n[ESCキーが押されました - 終了します]")
                exit_flag.set()
                return False  # これでキーボードリスナーも終了
        except Exception as e:
            print(f"[キーボードエラー]\n{traceback.format_exc()}")

    # マウスとキーボードのリスナーを並列で動かす
    with mouse.Listener(on_click=on_click) as mouse_listener, \
        keyboard.Listener(on_press=on_press) as keyboard_listener:
        exit_flag.wait()  # どちらかがexit_flagを立てたら終了

    # リスナー設定
    with mouse.Listener(on_click=on_click) as m_listener, \
        keyboard.Listener(on_press=on_press) as k_listener:

        if not once:
            escape_str = ' 終了: Esc'
        else:
            escape_str = ''
            
        print(f"\nクリック検知を開始しました。{escape_str}")
        print("======================================")

        # 終了フラグがセットされるまでメインスレッドをブロック
        while not exit_flag.is_set():
            time.sleep(0.1)


@instrumented(timer=True)
def find_element(queries, getAll=False):
    global app
    parent_windows = app.windows()  # すべてのトップレベルウィンドウを取得
    elems = []
    sep = getParam('ui.query_sep', ';')
    query_list = [q.strip() for q in queries.split(sep)]

    max_retry = getParam('ui.find_max_retry')
    interval  = getParam('ui.find_retry_interval')
    search_count = 0
    while search_count < max_retry:
        for win in parent_windows:
            elems.append(win)
            elems.extend(win.descendants())
            for query in query_list:
                query = query.strip()

                # 各種一致条件（順番に評価）
                filters = [
                    lambda e: e.element_info.automation_id == query,      # Automation ID で一致
                    lambda e: e.friendly_class_name() == query,           # クラス名で一致
                    lambda e: e.element_info.name == query,               # 名前(name)で一致
                    lambda e: e.window_text() == query,                   # タイトル(window text)で一致
                ]

                # フィルタを順に適用し、マッチする要素があれば elems を絞り込む
                for f in filters:
                    filtered = [e for e in elems if f(e)]
                    if filtered:
                        elems = filtered
                        break
                else:
                    # すべての条件に一致しなければ要素は見つからなかったとみなし、空リストに
                    elems = []
                    break
        if elems != []:
            break
        time.sleep(interval)

    if getAll:
        return elems
    
    index = getParam('ui.find_index')
    if index < len(elems):
        return elems[index]
    else:
        logger.warning(f'要素が見つかりませんでした: {query} index={index}')
        return None
    

@instrumented()
@retryCounter(max_retry=20, retry_interval=0.5, breakException=[KeyboardInterrupt, ElementNotFoundError])
def clickAction(query, double=False):
    # 要素検索
    element = find_element(query)
    if element is None:
        raise TimeoutError(f"指定した要素が見つかりませんでした: {query}")
    
    try:
        # 可視性と有効状態を確認
        if element.is_visible() and element.is_enabled():
            if double:
                element.click_input(double=double)
                return
                
            try:
                # 最初にinvoke()を試す（コントロールのデフォルトアクション）
                element.invoke()
                return
            except AttributeError:
                try:
                    # 次にclick()を試す（WM_CLICKメッセージ送信）
                    element.click()
                    return
                except AttributeError:
                    # 最後の手段としてclick_input()
                    element.click_input()
                    return
    except:
        raise

def dbClickAction(query):
    clickAction(query, double=True)


@instrumented()
def inputAction(query_text, escape=True, hotkey=False):
    
    def escape_for_sendkeys(text):
        """
        pywinauto.keyboard.SendKeys 用の特殊記号エスケープ関数
        """
        special_chars = ['+', '^', '%', '~', '(', ')', '{', '}']
        escaped = ''
        for char in text:
            if char in special_chars:
                escaped += f'{{{char}}}'
            else:
                escaped += char
        return escaped
    
    query, text = query_text.split(getParam('sep', ','))
    query = query.strip()
    text  = text.strip()
    
    type_interval = getParam('ui.type_interval', 0.01)
    if escape:
        text = escape_for_sendkeys(text)
    
    start_time = time.time()
    timeout = getParam('timeout', 10)
    while time.time() - start_time < timeout:
        # 要素検索
        element = find_element(query)
        if element:
            try:
                # 可視性と有効状態を確認
                if element.is_visible() and element.is_enabled():
                    element.set_focus()
                    time.sleep(Timings.after_setfocus_wait)
                    
                    # 特殊キー対応（Ctrl+Cなど）
                    send_keys(text, pause=type_interval)
                    return
                else:
                    print("要素が非表示または無効状態です")
            except Exception as e:
                raise



@instrumented()
def editAction(query_text):
    query, text = query_text.split(getParam('sep', ','))
    query = query.strip()
    text  = text.strip()
    
    start_time = time.time()
    timeout = getParam('timeout', 10)
    while time.time() - start_time < timeout:
        # 要素検索
        element = find_element(query)
        if element:
            try:
                # 可視性と有効状態を確認
                if element.is_visible() and element.is_enabled():
                    element.set_edit_text(text)
                    return
                else:
                    print("要素が非表示または無効状態です")
            except Exception as e:
                raise


@instrumented()
def targetAction(window_name=None):
    global app
    
    # デスクトップ上の全ウィンドウを取得
    windows = Desktop(backend="uia").windows()
    if not window_name:
        # すべてのトップレベルウィンドウを取得

        for win in windows:
            print(f"タイトル: {win.window_text()}, プロセスID: {win.process_id()}, クラス名: {win.element_info.class_name}")
        return
    
    target_pid = None
    
    start_time = time.time()
    timeout = getParam('timeout', 10)
    while time.time() - start_time < timeout and target_pid is None:
        for w in windows:
            if w.window_text() == window_name:
                target_pid = w.process_id()
                break

    if target_pid is None:
        raise

    # プロセスIDでApplicationに接続
    app = Application(backend='uia').connect(process=target_pid)


@instrumented()
@retryCounter(max_retry=20, retry_interval=0.5)
def connectAction(window_name=None):
    global app
    
    # デスクトップ上の全ウィンドウを取得
    windows = Desktop(backend="uia").windows()
    if not window_name:
        # すべてのトップレベルウィンドウを取得

        for win in windows:
            print(f"タイトル: {win.window_text()}, プロセスID: {win.process_id()}, クラス名: {win.element_info.class_name}")
        return
    
    target_pid = None
    
    for w in windows:
        if w.window_text() == window_name:
            target_pid = w.process_id()
            break
    else:
        raise ValueError(f"指定されたウィンドウ '{window_name}' が見つかりませんでした。")

    # プロセスIDでApplicationに接続
    app = Application(backend='uia').connect(process=target_pid)


@instrumented()
def getAction(query):
    start_time = time.time()
    timeout = getParam('timeout', 10)
    while time.time() - start_time < timeout:
        # 要素検索
        element = find_element(query)
        if element:
            automation_id = element.element_info.automation_id
            class_name    = element.friendly_class_name()
            name          = element.element_info.name
            text          = element.window_text()
            setParam('ui.automation_id', automation_id)
            setParam('ui.class_name'   , class_name)
            setParam('ui.name'         , name)
            setParam('ui.text'         , text)
            log_str = f'''
            element:{element} の情報を格納しました。
            ui.automation_id = {automation_id}
            ui.class_name    = {class_name}
            ui.name          = {name}
            ui.text          = {text}
            '''.strip()
            logger.info(log_str)
            return text

@instrumented()
def killAction():
    global app
    if app:
        app.kill()
        app = None
    else:
        logger.error(f'アプリが指定されていません')
        raise

action_list = {
    'run': runAction,
    'tree': treeAction,
    'inspect': inspectAction,
    'inspector': inspectorAction,
    'click': clickAction,
    'doubleClick': dbClickAction,
    'dbClick': dbClickAction,
    'input'  : inputAction,
    'target' : targetAction,
    'edit' : editAction,
    'kill' : killAction,
    'get'  : getAction,
    'connect': connectAction
}