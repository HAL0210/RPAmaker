import module.defaultActions    as defaultM
import module.flowActions       as flowM
import module.playwrightActions as pageM
import module.keyboardActions   as keyboardM
import module.soundActions      as soundM
import module.datetimeActions   as datetimeM
import module.uiActions         as uiM
import module.extraActions      as extraM


# 正式名称（正式なモジュール名→アクションリスト）
# 注意:Action名と重複が無いようにすること
formal_module_list = {
    'default' : defaultM,
    'flow'    : flowM,
    'keyboard': keyboardM,
    'page'    : pageM,
    'ui'      : uiM,
    'datetime': datetimeM,
    'sound'   : soundM,
    'extra'   : extraM,
}

# 別名（別名→正式名称）
alias_module_list = {
    'd' : 'default',
    'p' : 'page',
    's' : 'sound',
    'k' : 'keyboard',
    'dt': 'datetime',
    'u' : 'ui',
}

def getModuleList():
    # 最初は正式リストをコピー
    module_list = formal_module_list.copy()

    # エイリアスを追加
    for alias, formal in alias_module_list.items():
        if formal in formal_module_list:
            module_list[alias] = formal_module_list[formal]

    return module_list


module_list = getModuleList()

def getModuleActions(module):
    return module_list[module].action_list

def getModuleDescription(module):
    return module_list[module].__doc__