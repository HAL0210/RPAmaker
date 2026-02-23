'''既定で読み込まれる汎用コマンド(d)
'''

from lib.paramSetting import showAllParams, showParam
import subprocess
from lib.commonDefine import *

loadParams('mod/default.yaml')
logger = getMyLogger(__name__)

@instrumented()
def printAction(string=''):
    """指定された文字列をコンソールに出力
    
    Args:
        string (str): 出力する文字列
    
    Returns:
        String

    Examples:
        >>> print: hello,world!
        コンソール出力:hello,world!
        
    Note:
        ログには表示されません
    """
    print(string)
    return string

@instrumented()
def setAction(set_str=None, cast_type=None):
    """パラメータの取得または設定

    set_str の形式に応じて、パラメータの取得または設定を行います。
    - 'key=value' の形式で渡された場合は指定のパラメータを設定します。
    - 引数を指定しない場合は全パラメータを表示します。

    Args:
        set_str (str, optional): 'key=value' 形式の文字列。None の場合は全パラメータを表示します。
        cast_type (:obj:`type`, optional): 型変換に使用される型。
        - setInt, setFloat, setStr, setBoolで使用される。

    Returns:
        str or None: 設定された値。set_strがNoneの場合は None

    Examples:
        setコマンド
        >>> set: username=admin
        パラメータ'username'にadminが設定される
        設定される型は以下のフローで決定する
        1. 定義済みのパラメータの場合
        ⇒元Valueと同じ型
        2. 元Valueと同じ型に変換できないor未定義の場合
        ⇒文字列
        
        set[Type]コマンド
        >>> setInt  : timeout=1
        >>> setFloat: timeout=1
        >>> setBool : timeout=1
        >>> setStr  : timeout=1
        パラメータ'timeout'に各型にキャストされた1が設定される
        
        set(引数無し)
        >>> set
        全パラメータが表示される（戻り値は None）
    """
    if not set_str:
        showAllParams()
        return
    
    key, value = patternMatchSplit('=', set_str)
    
    setParam(key, value, cast_type=cast_type)
    return getParam(key)

def setIntAction(set_str):
    '''パラメータの設定(Int型)
    詳細は'set'を参照
    '''
    return setAction(set_str, cast_type=int)

def setFloatAction(set_str):
    '''パラメータの設定(Float型)
    詳細は'set'を参照
    '''
    return setAction(set_str, cast_type=float)

def setStrAction(set_str):
    '''パラメータの設定(Str型)
    詳細は'set'を参照
    '''
    return setAction(set_str, cast_type=str)

def setBoolAction(set_str):
    '''パラメータの設定(Bool型)
    詳細は'set'を参照
    '''
    return setAction(set_str, cast_type=bool)


@instrumented(timer=True)
def cmdAction(command=''):
    """シェルコマンドを実行する（シェル使用）

    Args:
        command (str): 実行するシェルコマンド

    Returns:
        int: コマンドの終了コード（0: 正常終了、0以外: エラー）

    Params:
        stdout (str): コマンドの標準出力（setParamで設定）
        stderr (str): コマンドの標準エラー出力（setParamで設定）
        returncode (int): コマンドの終了コード（setParamで設定）

    Note:
        shell=True を使用しているため、コマンドインジェクションなどのセキュリティリスクに注意が必要。
    """
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True  # 出力を bytes ではなく str で取得
    )
    setParam('stdout', result.stdout)
    setParam('stderr', result.stderr)
    setParam('returncode', result.returncode)
    
    logger.info(f"[cmdAction] Return Code: {result.returncode}")
    logger.info(f"[cmdAction] STDOUT:\n{result.stdout}")
    logger.info(f"[cmdAction] STDERR:\n{result.stderr}")
    
    return result.returncode


@instrumented()
def execAsyncAction(command):
    """コマンドをサブプロセスで非同期実行する（シェル不使用）

    Args:
        command (str): カンマ区切りのコマンドと引数（例: "python, script.py"）

    Returns:
        pid (int): 実行されたプロセスのPID

    Params:
        pid (int): 実行されたプロセスのPID（setParamで設定）

    Note:
        非同期実行されるため、終了コードや出力を取得するには別途管理が必要。
        `shell=False` を使用しており、引数の扱いには注意が必要。
    """
    sep = getParam('sep', ',')
    command_list = [arg.strip() for arg in command.split(sep)]
    proc = subprocess.Popen(command_list, shell=False)
    setParam('pid', proc.pid)
    
    logger.info(f"[execAsyncAction] PID: {proc.pid}")
    
    return proc.pid


@instrumented(timer=True)
def execAction(command):
    """コマンドを同期実行し、出力を取得して完了まで待機する（シェル不使用）

    Args:
        command (str): カンマ区切りのコマンドと引数

    Returns:
        int: コマンドの終了コード

    Params:
        stdout (str): 標準出力
        stderr (str): 標準エラー出力
        returncode (int): 終了コード
        pid (int): プロセスID

    Note:
        コマンド完了までブロックされ、出力も取得します。
    """
    sep = getParam('sep', ',')
    command_list = [arg.strip() for arg in command.split(sep)]

    proc = subprocess.Popen(
        command_list,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    setParam('pid', proc.pid)
    stdout, stderr = proc.communicate()
    setParam('stdout', stdout)
    setParam('stderr', stderr)
    setParam('returncode', proc.returncode)
    
    logger.info(f"[execAction] PID: {proc.pid}")
    logger.info(f"[execAction] Return Code: {proc.returncode}")
    logger.info(f"[execAction] STDOUT:\n{stdout}")
    logger.info(f"[execAction] STDERR:\n{stderr}")

    return proc.returncode


@instrumented()
def loadAction(file_path):
    """パラメータファイルを読み込む
    
    Args:
        file_path (str): 読み込むファイルのパス
        
    Returns:
        None
    
    Raises:
        FileNotFoundError: ファイルが存在しない場合
        SyntaxError: ファイル形式が不正な場合
    
    Note:
        PARAM_FOLDER内のyamlファイルは起動時に読み込まれる。
        それ以外のファイルを読み込みたい場合に使用すること。
    """
    if not os.path.isfile(file_path):
        logger.error(f"ファイルが見つかりません: {file_path}")
        raise FileNotFoundError(f"指定されたファイルが存在しません: {file_path}")

    try:
        loadParams(file_path)
        return None
    except SyntaxError as ve:
        logger.error(f"パラメータファイルの形式に誤りがあります: {file_path}")
        raise SyntaxError(f"パラメータファイル '{file_path}' の書式が不正です") from ve
    except Exception as e:
        logger.critical(f"ファイル読み込み中に予期せぬエラーが発生しました: {file_path}")
        sys.exit()


@instrumented(timer=True)
def waitAction(wait_time=None):
    """指定時間スリープする
    
    Args:
        wait_time: 待機時間（秒）。floatに変換される
    
    Returns:
        None
    
    Params:
        default_wait_time: wait_timeを指定せずに実行した場合の待機時間（秒）
    """
    if wait_time is None:
        wait_time = getParam('default_wait_time', 1)
    time.sleep(float(wait_time))

@instrumented()
def evalAction(command):
    """Python式を評価し結果をreturnパラメータに格納
    
    Args:
        command (str): 評価するPython式
        
    Returns:
        pythonの実行結果
        
    Examples:
        >>> eval: 1 + 2
        return 3
        
    Note:
        既定で読み込まれているライブラリ以外を使ったコマンドは実行不可
        日付(datetimeモジュール)を扱いたい時はdt.evalを利用すること
    """
    result = eval(command)
    setParam('return', result, disable_cast=True)
    logger.info(f'returnパラメータに{result}を格納しました')
    return result

@instrumented()
def boolAction(value=None):
    """指定された値をTrue/Falseに変換する。

    説明:
        入力された文字列を以下のルールで真偽値に変換します。
        - "a=b"   → a と b が等しいか判定
        - "a!=b"  → a と b が異なるか判定
        - 上記以外 → false_list に含まれているかどうかで判定

    Args:
        value (str, optional): 判定する対象の値。Noneの場合はfalse_listを表示する。

    Returns:
        bool or None: 判定結果のTrue/Falseを返す。valueがNoneの場合はNoneを返す。

    Raises:
        なし

    Examples:
        >>> bool: yes
        True
        >>> bool: false
        False
        >>> bool: apple=apple
        True
        >>> bool: dog!=cat
        True
        >>> bool
        falseと判定される文字列のリストが表示されます

    Note:
        false_list に含まれる値（例: "false", "no", "0", ""）はFalseと見なされます。
        この判定方法はifコマンドと同じ処理となっています。
    """
    if value is None:
        print(f'false_list:{false_list}')
        return
    
    result = toBool(str(value), enable_print=True)
    return result

@instrumented()
def checkAction(check=None):
    """ブール値の確認または入力待機を行う

    引数が与えられた場合はブール値に変換して確認し、False 相当であれば例外を発生させます。
    が与えられない場合は、ユーザー入力を待機します。

    Args:
        check (:obj:`str`, optional): ブール値として評価される文字列。

    Returns:
        None
    
    Raises:
        Exception: `check` が False 相当であった場合に例外を発生させます。

    Examples:
        >>> checkAction("true")
        "true" is True
        True

        >>> checkAction("no")
        Traceback (most recent call last):
        ...
        Exception: "no" is False

        >>> checkAction()
        Enter...  # 入力待機

    Note:
        `check` の評価についてはboolコマンドを確認してください。
    """
    if check is None:
        input('Enter...')
        return
    
    result = toBool(str(check), enable_print=False)
    if result:
        print(f'"{check}" is True')
        return
    else:
        raise Exception(f'"{check}" is False')


@instrumented()
def readAction(file_path_args):
    """コマンドファイルを読み込んで実行する
    
    Args:
        file_path (str): 実行するコマンドファイルのパス
    """
    file_path, *args = sepSplit(file_path_args, split=0)
    for arg in args:
        if '=' in arg:
            setAction(arg)
        else:
            raise Exception(f'第二引数以降はkey=valueの形式にしてください')
        
    # 循環参照防止のため関数内でインポート
    from readLines import readFile

    search_dir = getParam('COMMAND_FOLDER', '')
    join_path = os.path.join(search_dir, file_path)
    
    if   os.path.isfile(file_path):
        target_file = file_path
    elif os.path.isfile(join_path):
        target_file = join_path
    else:
        raise FileNotFoundError(f"ファイルが見つかりません: '{file_path}' or '{join_path}'")

    readFile(target_file)


@instrumented()
def needAction(key):
    """指定パラメータの存在を確認し、未設定なら例外を発生させる

    Args:
        key (str): 必須パラメータのキー名

    Raises:
        Exception: パラメータが未設定の場合に発生
    """
    if hasParam(key):
        logger.error(f'パラメータ"{key}"が設定されていません')
        raise Exception(f'parameter {key} is necessary')


@instrumented()
def quitAction(code=0):
    """アプリケーションを終了する

    Args:
        code (int, optional): 終了ステータスコード（デフォルトは 0）

    Note:
        通常終了には 0、異常終了には 1 などの非ゼロ値を指定します。
    """
    sys.exit(code)

@instrumented()
def helpAction(search=None):
    """ヘルプ情報の表示
    """
    from moduleList import module_list, formal_module_list, getModuleActions, getModuleDescription
    if search:
        if search in module_list:
            target_actions = getModuleActions(search)
            doc_dict = {
                key: (value.__doc__.strip().splitlines()[0] if value.__doc__ else 'on going')
                for key, value in target_actions.items()
            }
            length = tableDisplay(doc_dict, sort=False)
            print('各コマンドの仕様については、help:コマンド で確認できます')
            print('module_priorityに登録されていないモジュールの場合はmodule.command で呼び出してください')

        else:
            from readLines import resolveCommand
            try:
                command_func = resolveCommand(search)
                doc = command_func.__doc__
                print(doc)
            except KeyError:
                logger.error(f'helpコマンドで{search}がヒットしませんでした。')
                raise
    else:
        doc_dict = {}
        for module in formal_module_list.keys():
            doc = getModuleDescription(module)
            if doc:
                first_line = doc.strip().splitlines()[0]
            else:
                first_line = "on going"
            doc_dict[module] = first_line
        length = tableDisplay(doc_dict, key_name='Module', value_name='Description(alias)', sort=False)
        print()
        print('各モジュールのコマンドについては、help:モジュール名 で確認できます')
        print('-' * length)
        importAction()

@instrumented()
def importAction(module=None):
    """モジュールの優先度設定を取得または変更する関数

    現在のモジュール優先度（module_priority）を取得、または指定されたモジュールを優先度の先頭に設定します。
    優先度設定は、RPA処理の中でアクションルーティング時に参照されます。

    Args:
        module (:obj:`str`, optional): 優先的に使用するモジュール名。
            - `None` の場合：現在の優先度と利用可能なモジュール一覧を表示します。
            - モジュール名を指定した場合：該当モジュールを優先度の先頭に追加します。

    Returns:
        str: 更新後または取得したモジュール優先度文字列。

    Raises:
        KeyError: 指定されたモジュール名が `module_list` に存在しない場合。

    Examples:

        現在の優先度を確認：
        >>> import
        ↓コンソール出力
        モジュール優先度:d,k
        利用可能なModule(別名含む):'d', 'default', 'p', ...

        モジュール 'ui' を優先度の先頭に設定：
        >>> import: ui

    Note:
        - 利用可能なモジュールは `moduleList.module_list` により定義されます。
        - コマンド名称に重複がある場合、優先度における先頭側から順に優先されます。
    """
    from moduleList import module_list
    module_priority = getParam('module_priority')
    if module is None:
        print(f'モジュール優先度:{module_priority}')
        print(f'上記に含まれるモジュールのコマンドはモジュール名を付けずに指定可能です。')
        print(f'コマンド名が重複している場合は先頭のモジュールが優先されます。')
        print(f'含まれないモジュールを利用する場合は モジュール名.コマンド として指定可能です。')
        return module_priority
    
    if module in module_list:
        module_priority = module + ',' + module_priority
        setParam('module_priority', module_priority)
        return module_priority
    
    logger.error(f'{module}は利用可能なモジュールに含まれません')
    raise KeyError(f'{module} not in module_list')


def hideAction():
    """一つ下のコマンドの引数をログで非表示にする

    Examples:
        >print: password
        2025/05/23 05:14:18.558 [INFO]  | → Run    executeLine(action='print', args='password')
        password
        2025/05/23 05:14:18.559 [INFO]  | ← Done   executeLine(action='print', args='password')
        >hide
        2025/05/23 05:13:10.974 [INFO]  | → Run    executeLine(action='hide', args='')
        2025/05/23 05:13:10.976 [INFO]  | ← Done   executeLine(action='hide', args='')
        >print: password
        2025/05/23 05:13:23.454 [INFO]  | → Run    executeLine(***)
        password
        2025/05/23 05:13:23.456 [INFO]  | ← Done   executeLine(***)
    """
    setParam('temp_hide', True)

# キーに指定された関数を返す
action_list = {
    'print': printAction,
    'set':   setAction,
    'setInt':   setIntAction,
    'setFloat':   setFloatAction,
    'setStr':   setStrAction,
    'setBool':   setBoolAction,
    'wait':  waitAction,
    'load':  loadAction,
    'read':  readAction,
    'cmd':   cmdAction,
    'exec':  execAction,
    'execAsync':  execAsyncAction,
    'eval':  evalAction,
    'quit':  quitAction,
    'help': helpAction,
    'import': importAction,
    'bool': boolAction,
    'check': checkAction,
    'hide': hideAction,
}
