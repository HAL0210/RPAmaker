import sys
import time
import re
from system.paramSetting import getParam, setParam
from module.flowActions import flow_action_list
from system.decoratorSetting import *
from system.customException import *
from system.commonDefine import *
from system.loggerSetting import logger

from moduleList import module_list, getModuleActions

@instrumented()
def selectAction(action):
    
    pattern = r'^(.+?)\.(.*)$'
    match = re.search(pattern, action)
    if match:
        module = match.group(1).strip()
        action = match.group(2).strip()
        module_actions = getModuleActions(module)
        if action in module_actions:
            return module_actions[action]
        else:
            raise KeyError('コマンドが見つかりません')
    else:
        module_priority = getParam('module_priority', 'd').split(',')
        for module in module_priority:
            module_actions = getModuleActions(module)
            if action  in module_actions:
                return module_actions[action]
        else:
            raise KeyError('コマンドが見つかりません')

@instrumented()
def executeLine(action, args):
    # 変数置換
    pattern = r'\$\{(.+?)\}'
    match = re.search(pattern, args)
    if match:
        key = match.group(1)
        if hasParam(key):
            value = str(getParam(key))
            new_args = args.replace(f'${{{key}}}', value)
            logger.info(f'変数を置換しました : ${{{key}}} -> {value}')
            executeLine(action, new_args)
            return
        else:
            logger.warning(f'変数を置換できません : ${{{key}}} -> {value}')
            
    # 変数置換
    pattern = r'\$\{(.+?)\}'
    match = re.search(pattern, action)
    if match:
        key = match.group(1)
        if hasParam(key):
            value = str(getParam(key))
            new_action = action.replace(f'${{{key}}}', value)
            logger.info(f'変数を置換しました : ${{{key}}} -> {value}')
            executeLine(new_action, args)
            return
        else:
            logger.warning(f'変数を置換できません : ${{{key}}} -> {value}')

    # フロー制御 or 通常アクション
    try:
        # アクション関数を取得
        if action in flow_action_list:
            actionFunc = flow_action_list[action]
        else:
            # スキップ対象の通常アクションは実行しない
            flow_stack = getParam('flow_stack', [])
            is_skipping = any(not frame['executed'] for frame in flow_stack)
            if is_skipping:
                return
            if '=' in action:
                actionFunc = selectAction('set')
                args = action
            else:
                actionFunc = selectAction(action)
                
        if args:
            result = actionFunc(args)
        else:
            result = actionFunc()

        if result is not None:
            setParam('return', result, disable_cast=True)
            
    except KeyboardInterrupt as e:
        raise
    except Exception as e:
        logger.error(f"Error in executeLine: {e}")
        raise


def readLine(line):
    line = line.strip()
    # 空行ならば処理なし
    if line == '':
        return
    
    # #始まりならばコメントアウト
    if line.startswith('#'):
        return
    
    # コマンド：引数の分離
    action, args = patternMatchSplit(':', line)
    
    # flow_stack ベースで「スキップすべき通常アクションかどうか」を判断
    flow_stack = getParam('flow_stack', [])
    is_skipping = any(not frame['executed'] for frame in flow_stack)

    if is_skipping and action not in flow_action_list:
        logger.debug(f'skipped({line})flow_stack:{flow_stack}')
        return
        
    executeLine(action, args)


@instrumented()
def readFile(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError as e:
        raise FileNotFoundError(f'指定されたファイルが見つかりません: "{file_path}"')
    
    for line in lines:
        line = line.strip()
        try:
            readLine(line)
        except Exception as e:
            logger.error(f'実行に失敗 : {line}', exc_info=True)
            raise
        except KeyboardInterrupt as e:
            logger.warning('KeyboardInterrupt')
            break
        except SystemExit as e:
            logger.info('SystemExit')
            break
        time.sleep(float(getParam('READ_LINE_INTERVAL')))


def interactiveMode():
    while True:
        try:
            line = input('>').strip()
        except (KeyboardInterrupt, EOFError) as e:
            print()
            break  # ループを抜けて終了
        try:
            readLine(line)
        except KeyboardInterrupt:
            logger.warning('KeyboardInterrupt')
        except SystemExit:
            logger.info('SystemExit')
            break
        except Exception as e:
            logger.error(f'実行に失敗 : {line}', exc_info=True)
