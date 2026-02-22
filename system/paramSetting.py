import pyperclip
import re
import os
from ruamel.yaml import YAML

parameters = {}

def setParam(key, value, cast_type=None, disable_cast=False):
    from system.customFunction import toBool
    if disable_cast:
        parameters[key] = value
        return
    
    if cast_type is not None:
        parameters[key] = cast_type(value)
    
    # 定義済みの場合、型を変換しない
    if hasParam(key):
        cast_type = type(getParam(key))
        try:
            if cast_type is bool:
                value = toBool(str(value))
            else:
                value = cast_type(str(value))
        except (ValueError, TypeError) as e:
            raise
    
    parameters[key] = value

def getParam(key, default_value=None, cast_type=None):
    value = None
    if key in reservedParams:
        value = reservedParams[key]()
    elif hasParam(key):
        value = parameters[key]
    elif default_value is not None:
        value = default_value
        setParam(key, value)
            
    if value is None:
        raise KeyError(f"パラメータ '{key}' が設定されていません。")
    
    if not cast_type:
        return value
    try:
        if cast_type is bool:
            # Boolの時はfalse_listに含まれるものはFalseとするように変換
            from system.customFunction import false_list
            return str(value).strip().lower() not in false_list
        return cast_type(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"パラメータ '{key}' を {cast_type.__name__} に変換できません: {e}")


def getReservedParams(key):
    # PCのクリップボード(コピー)内容を返却
    if key == 'clip':
        return pyperclip.paste()
    
    # コマンドラインで入力を受け付ける
    if key == 'input':
        if getParam('AUTO_DEFAULT_INPUT'):
            return getParam('default')
        if getParam('ENABLE_DEFAULT_INPUT'):
            default_input = getParam('default')
            user_input = input(f'(input:default={default_input})>')
            if user_input:
                return user_input
            else:
                return default_input
        else:
            user_input = input('(input)>')
            return user_input
    else:
        return parameters[key]
        

def getClip():
    result = pyperclip.paste()
    result = re.sub(r'\r\n?|\n', r'\n', result)
    return result

def getInput():
    if getParam('AUTO_DEFAULT_INPUT'):
        return getParam('default')
    if getParam('ENABLE_DEFAULT_INPUT') and hasParam('default'):
        default_input = getParam('default')
        user_input = input(f'(input:default={default_input})>')
        if user_input:
            return user_input
        else:
            return default_input
    else:
        user_input = input('(input)>')
        return user_input


def loadParams(file_path, encoding='utf-8'):
    yaml = YAML()
    yaml.preserve_quotes = True

    search_dir = getParam('PARAM_FOLDER', '')
    full_path = os.path.join(search_dir, file_path)
    
    if   os.path.isfile(file_path):
        target_file = file_path
    elif os.path.isfile(full_path):
        target_file = full_path
    else:
        raise FileNotFoundError(f"ファイルが見つかりません: '{file_path}' or '{full_path}'")
    
    with open(target_file, 'r', encoding=encoding) as f:
        data = yaml.load(f)

    def recursive_update(d, parent_key=''):
        updated = False
        for k, v in d.items():
            key_path = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                if recursive_update(v, key_path):
                    updated = True
            elif v == '?':
                new_value = input(f"「{key_path}」の値を入力してください: ")
                d[k] = new_value
                updated = True
                setParam(key_path, new_value)
            else:
                setParam(key_path, v)
        return updated

    updated = recursive_update(data)
    if updated:
        with open(file_path, 'w', encoding=encoding) as f:
            yaml.dump(data, f)



def hasParam(key):
    return key in parameters or key in reservedParams

def showAllParams():
    for key in parameters:
        showParam(key)

def showParam(key):
    if hasParam(key):
        print(f'{key}={getParam(key)}')
    else:
        print(f'{key}は設定されていません')

reservedParams = {
    'clip' : getClip,
    'input': getInput,
    '?'    : getInput,
}