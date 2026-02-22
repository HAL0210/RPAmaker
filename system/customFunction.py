import re
import sys
from system.loggerSetting import getMyLogger
from system.paramSetting  import getParam, setParam



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
    """
    文字列を指定されたセパレータで分割する。

    Args:
        args (str): 分割対象の文字列。
        sep (str, optional): 区切り文字。None の場合、getParam('sep', ',') を使用。
        strip (bool): 各要素を strip() するかどうか。
        split (int): 必要な要素数。0 の場合、制限なし。足りない場合は空文字で埋める。

    Returns:
        list[str]: 分割された文字列リスト。

    Raises:
        ValueError: 要素数が split を超えた場合。
    """
    if sep is None:
        sep = getParam('sep', ',')

    parts = args.split(sep)

    if strip:
        parts = [a.strip() for a in parts]

    if split > 0:
        if len(parts) > split:
            raise ValueError(f"分割数が指定({split})を超えました: {len(parts)}個に分割されました")
        # 足りなければ空文字を追加
        while len(parts) < split:
            parts.append('')
    
    return parts

from wcwidth import wcswidth

def tableDisplay(dictionary, key_name='Key', value_name='Value', sort=True):
    # キー名の特殊ソート処理（f1, f2,...を数値順に）
    def sort_key(item):
        key = item[0]
        if key.startswith('f') and key[1:].isdigit():
            return (0, int(key[1:]))  # f系を数値でソート
        return (1, key)  # その他はアルファベット順


    # 表示用データ生成
    if sort:
        items = sorted(dictionary.items(), key=sort_key)
    else: 
        items = dictionary.items()

    # 見た目の幅を計算（wcswidthを使う）
    def get_display_width(text):
        return wcswidth(str(text))

    max_key_len = max(get_display_width(f"'{k}'") for k in dictionary) + 2  # 余白追加
    max_val_len = max(get_display_width(v) for v in dictionary.values()) + 2

    # 表のヘッダーを整形
    header = "| {:<{}} | {:<{}} |".format(
        key_name, max_key_len,
        value_name, max_val_len
    )
    separator = "+-{}-+-{}-+".format(
        '-' * max_key_len,
        '-' * max_val_len
    )

    # 表示実行
    print(separator)
    print(header)
    print(separator)
    for k, v in items:
        key_text = f"'{k}'"
        val_text = str(v)

        # 幅調整（日本語対応）
        key_padding = max_key_len - get_display_width(key_text)
        val_padding = max_val_len - get_display_width(val_text)

        print(f"| {key_text}{' ' * key_padding} | {val_text}{' ' * val_padding} |")
    print(separator)
    
    return len(header)


false_list = ['false', 'undefined', 'no', 'none', 'null', '0', 'off', '']

def toBool(value, enable_print=False):
    """
    文字列からブール値に変換する。

    特別な形式:
        "a=b"   → a == b
        "a!=b"  → a != b
        その他  → false_list に含まれていないかで判定

    Args:
        value (str): 判定対象の文字列
        enable_print (bool): 判定結果を標準出力するか

    Returns:
        bool: 判定結果
    """
    # not equal判定
    arg1, arg2 = sepSplit(value, sep='!=', strip=True, split=2)
    if arg2 != '':
        result = arg1 != arg2
        if enable_print: print(result)
        return result
    
    # equal判定
    arg1, arg2 = sepSplit(value, sep='=', strip=True, split=2)
    if arg2 != '':
        result = arg1 == arg2
        if enable_print: print(result)
        return result
    
    # Bool変換判定
    result = str(value).strip().lower() not in false_list
    if enable_print: print(result)
    return result


import urllib.parse

def encode_url_component(text: str) -> str:
    """文字列をURLエンコードする（すべての記号を対象）"""
    return urllib.parse.quote(text, safe='')

def decode_url_component(encoded_text: str) -> str:
    """URLエンコードされた文字列をデコードする"""
    return urllib.parse.unquote(encoded_text)
