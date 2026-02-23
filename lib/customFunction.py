import re
import sys
from lib.loggerSetting import getMyLogger
from lib.paramSetting  import getParam, setParam


def patternMatchSplit(separator, line):
    logger = getMyLogger(__name__)
    pattern = rf'^(.+?){re.escape(separator)}(.*)$'
    
    compiled = re.compile(pattern)

    # 1. グループ数を調べる
    num_groups = compiled.groups
    if num_groups != 2:
        logger.critical(f'パターン不正:{pattern}')
        sys.exit()
    
    # 2. マッチしたら分割
    match = re.search(pattern, line)
    if match:
        arg1 = match.group(1).strip()
        arg2 = match.group(2).strip()
    else:
        arg1 = line.strip()
        arg2 = ''
    
    return arg1, arg2


def sepSplit(args, sep=None, strip=True, split=2):
    if sep is None:
        sep = getParam('sep', ',')

    parts = args.split(sep)

    if strip:
        parts = [a.strip() for a in parts]

    if split > 0:
        if len(parts) > split:
            raise ValueError(f"分割数が指定({split})を超えました: {len(parts)}個に分割されました")
        while len(parts) < split:
            parts.append('')
    
    return parts

from wcwidth import wcswidth

def tableDisplay(dictionary, key_name='Key', value_name='Value', sort=True):
    def sort_key(item):
        key = item[0]
        if key.startswith('f') and key[1:].isdigit():
            return (0, int(key[1:]))
        return (1, key)

    if sort:
        items = sorted(dictionary.items(), key=sort_key)
    else: 
        items = dictionary.items()

    def get_display_width(text):
        return wcswidth(str(text))

    max_key_len = max(get_display_width(f"'{k}'") for k in dictionary) + 2
    max_val_len = max(get_display_width(v) for v in dictionary.values()) + 2

    header = "| {:<{}} | {:<{}} |".format(
        key_name, max_key_len,
        value_name, max_val_len
    )
    separator = "+-{}-+-{}-+".format(
        '-' * max_key_len,
        '-' * max_val_len
    )

    print(separator)
    print(header)
    print(separator)
    for k, v in items:
        key_text = f"'{k}'"
        val_text = str(v)

        key_padding = max_key_len - get_display_width(key_text)
        val_padding = max_val_len - get_display_width(val_text)

        print(f"| {key_text}{' ' * key_padding} | {val_text}{' ' * val_padding} |")
    print(separator)
    
    return len(header)


false_list = ['false', 'undefined', 'no', 'none', 'null', '0', 'off', '']

def toBool(value, enable_print=False):
    arg1, arg2 = sepSplit(value, sep='!=', strip=True, split=2)
    if arg2 != '':
        result = arg1 != arg2
        if enable_print: print(result)
        return result
    
    arg1, arg2 = sepSplit(value, sep='=', strip=True, split=2)
    if arg2 != '':
        result = arg1 == arg2
        if enable_print: print(result)
        return result
    
    result = str(value).strip().lower() not in false_list
    if enable_print: print(result)
    return result


import urllib.parse

def encode_url_component(text: str) -> str:
    return urllib.parse.quote(text, safe='')

def decode_url_component(encoded_text: str) -> str:
    return urllib.parse.unquote(encoded_text)
