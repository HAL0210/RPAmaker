# docstringの書式
def func(arg1, arg2):
    """概要

    詳細説明

    Args:
        引数(arg1)の名前 (引数(arg1)の型): 引数(arg1)の説明
        引数(arg2)の名前 (:obj:`引数(arg2)の型`, optional): 引数(arg2)の説明

    Returns:
        戻り値の型: 戻り値の説明

    Raises:
        例外の名前: 例外の説明

    Examples:

        関数の使い方

        >>> func(5, 6)
        11
    
    Params:（getParamで取得するパラメータやsetParamで設定されるパラメータの説明）
        parameters: 設定されたパラメータについて
        
    Note:
        注意事項や注釈など

    """
    result = arg1 + arg2
    return result

# ログレベル基準
CRITICAL = '動作に支障が出るし、どんな入力でも発生しない想定のもの'
ERROR    = '動作に支障が出るが入力次第で発生するもの'
WARNING  = '理想の動作ではないが支障はないもの'
INFO     = '普段使いで確認に値するもの'
DEBUG    = '上位レベルに該当しないもの'
