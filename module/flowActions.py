'''フロー制御のための特殊モジュール(詳細はflow.helpコマンド)

'''

from lib.commonDefine import *
logger = getMyLogger(__name__)

@instrumented()
def ifAction(arg=None):
    """
    if分岐処理を開始し、分岐判断を行う

    Args:
        arg (str): 分岐条件(詳細はboolコマンド)

    Returns:
        None
    """
    if arg is None:
        arg = ''

    result = toBool(arg)
    
    # push状態を記録（Trueならそのブロックを実行する）
    flow_stack = getParam('flow_stack', [])
    flow_stack.append({
        'executed': result,  # このブロックを実行するか
        'break': result      # 以降の elif/else をスキップするか
    })
    setParam('flow_stack', flow_stack, disable_cast=True)


@instrumented()
def elifAction(arg=None):
    """
    前のif,elif文で分岐していない場合、分岐判断を行う

    Args:
        arg (str): 分岐条件(詳細はboolコマンド)

    Returns:
        None

    Raises:
        Exception('elif without if'): if文外で呼び出された場合
        ValueError: 引数がない場合
    """
    flow_stack = getParam('flow_stack')
    if not flow_stack:
        raise Exception('elif without if')

    frame = flow_stack[-1]

    if frame['break']:
        frame['executed'] = False
        return  # すでに条件マッチしてる → 以降スキップ

    if arg is None:
        raise ValueError('elifには引数が必要です')

    result = toBool(arg)
    frame['executed'] = result
    frame['break'] = result
    setParam('flow_stack', flow_stack, disable_cast=True)


@instrumented()
def elseAction():
    """
    前のif,elif文で分岐していない場合に実行する

    Args:
        無し

    Returns:
        None

    Raises:
        Exception('else without if'): if文外で呼び出された場合
    """
    flow_stack = getParam('flow_stack')
    if not flow_stack:
        logger.error(f'elseコマンドはifの後で使用してください')
        raise Exception('else without if')

    frame = flow_stack[-1]

    if frame['break']:
        frame['executed'] = False
    else:
        frame['executed'] = True
        frame['break'] = True

    setParam('flow_stack', flow_stack, disable_cast=True)

    
@instrumented()
def fiAction():
    """
    if,elif,else文を終了させる

    Args:
        無し

    Returns:
        None

    Raises:
        Exception('fi without if'): if文外で呼び出された場合
    """
    flow_stack = getParam('flow_stack')
    if not flow_stack:
        logger.error(f'fiコマンドはifの後で使用してください')
        raise Exception('fi without if')

    flow_stack.pop()
    setParam('flow_stack', flow_stack, disable_cast=True)


def flowHelpAction(action=None):
    """フロー制御アクションのヘルプ情報を表示する。

    指定されたアクション（例: 'if', 'else' など）の詳細なヘルプを表示する。
    アクションを指定しない場合は、すべてのフローアクションの一覧を簡易表示する。

    Args:
        action (str, optional): 詳細ヘルプを表示したいアクション名。省略時は一覧表示。

    Raises:
        ValueError: 指定されたアクション名が存在しない場合。

    Examples:
        # 特定アクションのヘルプを見る
        >>> flow: if
        ifコマンドの詳細を出力

        # 全アクションの簡易一覧を見る
        >>> flowHelpAction()
        全フローアクションと説明を出力
    """
    if action:
        if action in flow_action_list:
            action = flow_action_list[action]
            doc = action.__doc__
            print(doc)
        else:
            logger.error(f'helpコマンドで{action}がヒットしませんでした。')
            raise ValueError(f'{action} not in flow_actions')
    else:
        doc_dict = {
            key: (value.__doc__.strip().splitlines()[0] if value.__doc__ else 'on going')
            for key, value in flow_action_list.items()
        }
        tableDisplay(doc_dict, sort=False)


action_list = {
    'help': flowHelpAction
}

flow_action_list = {
    'if': ifAction,
    'elif': elifAction,
    'else': elseAction,
    'fi': fiAction,
}