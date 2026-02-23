_shutdown_hooks = []

def register_shutdown_hook(func):
    """シャットダウン時に呼び出す関数を登録"""
    _shutdown_hooks.append(func)

def run_shutdown_hooks():
    """登録された全てのシャットダウン処理を実行"""
    for func in _shutdown_hooks:
        try:
            func()
        except Exception as e:
            print(f"[shutdown error] {func.__name__}: {e}")
