import sys
import os
import traceback
from lib.paramSetting import setParam, getParam, loadParams
from lib.loggerSetting import setLogger
from lib.decoratorSetting import instrumented

default_init_file_path = 'init.yaml'

def init(init_file_path):
    """指定された文字列をコンソールに出力する
    
    Args:
        init_file_path (str): 初期パラメータファイルのパス
    
    Raises:
        FileNotFoundError: ファイルが存在しない場合
    """
    
    # 初期パラメータの読込
    try:
        loadParams(init_file_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"初期パラメータファイル '{init_file_path}' の読み込みに失敗しました。\n詳細: {str(e)}")
    
    # バージョン表示
    major = getParam('version.major')
    minor = getParam('version.minor')
    patch = getParam('version.patch')
    version = f'{major}.{minor}.{patch}'
    setParam('version', version)

    # パラメータの読込
    param_dir = getParam('PARAM_FOLDER')
    for root, _, files in os.walk(param_dir):
        for filename in files:
            if filename.endswith('.yaml'):
                file_path = os.path.join(root, filename)
                loadParams(file_path)

    # ロガー設定
    try:
        setLogger()
    except Exception as e:
        raise Exception(f"ロガー設定の読み込みに失敗しました。\n詳細: {str(e)}")


@instrumented(log_level=20)
def commandRPA(version):
    """CommandRPAを実行する
    
    sys引数がある場合、第一引数をcommandファイルパスとして読み込む。
    sys引数がない場合、対話形式で実行するModeを呼び出す。
    
    Args:
        version (str): バージョン（出力表示のみで利用）
    
    Raises:
        *: 実行時の例外をそのままraiseする
    """
    print(f'--- CommandRPA Executing version:{version} ---')
    if len(sys.argv) > 1:
        # テキストファイルベースのRPA読み込み
        from readLines import readFile
        
        file_path = sys.argv[1]
        search_dir = getParam('COMMAND_FOLDER', '')
        full_path = os.path.join(search_dir, file_path)
        
        if   os.path.isfile(file_path):
            target_file = file_path
        elif os.path.isfile(full_path):
            target_file = full_path
        else:
            raise FileNotFoundError(f"ファイルが見つかりません: '{file_path}' or '{full_path}'")
        
        try:
            readFile(target_file)
        except:
            if getParam('auto_interactive_when_read_line_except', False):
                from readLines import interactiveMode
                interactiveMode()
            else:
                raise
            
    else:
        # 対話モード
        from readLines import interactiveMode
        interactiveMode()

# メイン実行
if __name__ == '__main__':
    # 第二引数(オプション)からparameterの読込を行う
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                key = key.strip()
                value = value.strip()
                setParam(key, value)
            else:
                raise Exception(f'第二引数以降はkey=valueの形式にしてください')
    
    # 初期化関数実行
    # 第二引数でinit_file_pathが指定された場合はそれを読み込む
    # 指定されていない場合はdefault_init_file_path(init.yaml)を読み込む
    init_file_path = getParam('init_file_path', default_init_file_path)
    init(init_file_path)
    version = getParam('version', 'invalid_version')
    
    try:
        # RPA処理実行
        commandRPA(version)
    except (KeyboardInterrupt, SystemExit):
        # 正常終了
        pass
    except:
        # 異常終了
        print(traceback.format_exc())
        print('異常終了しました。')
        input('Enter...')
    finally:
        # 終了時呼び出し実行
        from lib.shutdownSetting import run_shutdown_hooks
        run_shutdown_hooks()
