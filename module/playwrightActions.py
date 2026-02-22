'''Playwrightでブラウザ操作(p)
'''
from playwright.sync_api import sync_playwright
from lib.commonDefine import *

p       = None
browser = None
context = None
page    = None
loadParams('mod/playwright.yaml')
logger = getMyLogger(__name__)

@instrumented()
def initBrowser():
    global p, browser, context

    try:
        executable_path = getParam('p.browser.executable_path')
        if hasParam(f'app_path.{executable_path}'):
            executable_path = getParam(f'app_path.{executable_path}')
        is_headless = getParam('p.browser.is_headless')
    except:
        raise
    
    p = sync_playwright().start()
    register_shutdown_hook(stopBrowser)
    browser = p.chromium.launch(
        headless=is_headless,
        executable_path=executable_path
    )
    context = browser.new_context()

@instrumented()
def openAction(url, new_page=True):
    """指定されたURLをブラウザで開く（新規タブ）。

    説明:
        Playwrightのコンテキストからページを作成し、
        指定されたURLをブラウザで開きます。
        初回呼び出し時にブラウザが初期化されていなければ、ブラウザを起動します。
        また、ページ上で発生するダイアログ（アラート等）を自動で受け入れるか拒否するかを
        `dialog_auto_accept` パラメータにより制御します。

    Args:
        url (str): 移動先のURL文字列。内部で`urlParamSearch`を通して最終的なURLを確定します。
        new_page (bool): Trueの場合は新しいタブ（ページ）を開き、Falseの場合は既存のページを使用します。

    Returns:
        None

    Raises:
        なし

    Examples:
        >>> open: https://example.com
        ブラウザでURLを新しいタブで開きます

        >>> goto: https://example.com
        ブラウザでURLを現在有効なタブで開きます

        >>> open: 名称
        パラメータ 'url.名称' が設定されている場合、その取得値をURLとして開きます

    Params:
        - p.browser.dialog_auto_accept (bool): Trueの場合ダイアログを自動でaccept、Falseならdismissします。

    Note:
        グローバル変数`page`が未定義またはNoneなら、自動的に新しいタブを開きます。
        gotoコマンドではnew_page=Falseで呼ばれ、既存タブでURL遷移を行います。
    """
    global page
    if page is None:
        initBrowser()

    if new_page or page is None:
        page = context.new_page()

    dialog_auto_accept = getParam('p.browser.dialog_auto_accept', True)
    if dialog_auto_accept:
        page.on("dialog", lambda dialog: dialog.accept())
    else:
        page.on("dialog", lambda dialog: dialog.dismiss())

    url = urlParamSearch(url)
    page.goto(url)


@instrumented()
def gotoAction(url):
    """指定されたURLへ現在のブラウザタブで移動する。

    Note:
        詳細はopenコマンドを参照してください
    """
    openAction(url, new_page=False)

def urlParamSearch(url):
    if hasParam(f'url.{url}'):
        return getParam(f'url.{url}')
    else:
        return url

@instrumented()
def tabAction(num_str):
    """指定されたインデックスのタブ（ページ）に切り替える。

    説明:
        現在のブラウザコンテキスト内のページ一覧（タブ）から、
        指定されたインデックスのページをアクティブにし、前面に表示します。
        インデックスが範囲外の場合は例外を発生させます。

    Args:
        num_str (str): 切り替えたいタブのインデックス番号（文字列で渡す）。

    Returns:
        None

    Raises:
        Exception: 指定したインデックスのページが存在しない場合に例外が発生します。

    Examples:
        >>> tab: 1
        2番目のタブをアクティブに切り替えます。

    Note:
        インデックスは0から始まるため、1番目のタブはインデックス0になります。
    """
    global page
    index = int(num_str)
    pages = context.pages

    try:
        page = pages[index]
        page.bring_to_front()
    except:
        logger.warning('指定されたインデックスのタブがありません')
        raise


def searchElements(page, query):
    elements = []
    
    # まずメインページを探す
    elements.extend(page.locator(query).element_handles())

    # すべてのフレームで探す
    for frame in page.frames:
        try:
            elements.extend(frame.locator(query).element_handles())
        except Exception as e:
            # フレームが壊れてる場合など無視
            print(f"frame error: {e}")

    return elements



@instrumented(timer=True)
def getElement(page, query, no_retry=False):
    """Playwrightで汎用的に要素を取得する関数。

    説明:
        検索クエリとインデックス番号をカンマ区切りで指定し、
        Playwrightのページから対象要素を取得します。
        クエリの種類（XPath、CSS、Textなど）は自動で判別・補完されます。
        指定インデックスの要素が存在しない場合はTimeoutErrorを発生させます。

    Args:
        page: Playwrightのページオブジェクト。
        query (str): 検索クエリとインデックスをカンマ区切りで指定。
            例: `"//button[@id='login']"` → XPathで一致要素を取得。
                `"ログイン"` → テキスト一致の最初の要素を取得。

    Returns:
        ElementHandle: 見つかった対象の要素。

    Raises:
        TimeoutError: 要素が見つからない場合。
        KeyboardInterrupt: ユーザー中断（Ctrl+C）。

    Examples:
        >>> getElement(page, "ログイン")
        テキスト「ログイン」に一致する最初の要素を取得。

        >>> getElement(page, "//div[@class='item']")
        XPathで一致する要素を取得。

    Params:
        - p.max_retry (int): リトライ回数
        - p.retry_interval (int): リトライ間隔
    """
    
    # クエリを自動判定して補完する
    if query.startswith('/'):
        query = f'xpath={query}'
    elif query.startswith('#') or query.startswith('.') or query.startswith('['):
        query = f'css={query}'
    elif query.startswith('text=') or query.startswith('xpath=') or query.startswith('css=') or query.startswith('role='):
        pass  # すでに書き方OK
    else:
        # プレーンな文字列はテキスト検索扱いにする
        query = f'text="{query}"'

    # 実際に要素を検索する
    max_retry = getParam('p.find_max_retry')
    interval  = getParam('p.find_retry_interval')
    search_count = 0
    while search_count < max_retry:
        elements = searchElements(page, query)
        count = len(elements)
        index = getParam('p.find_index', 0)
        if index < count:
            element = elements[index]
            logger.debug(f'find_result: {element}')
            return element
        if no_retry:
            return None
        time.sleep(interval)
    
    logger.warning(f'要素が見つかりませんでした: {query} index={index}')
    return None


@instrumented()
@retryCounter(breakException=[KeyboardInterrupt, TimeoutError])
def clickAction(query):
    """Playwrightで要素をクリックする汎用アクション。

    説明:
        検索クエリとインデックス番号をカンマ区切りで指定し、
        Playwright上の対象要素をクリックします。
        クリック方法は `p.click_method` パラメータにより切り替えることができます。

    Args:
        query (str): 検索クエリを指定。

    Returns:
        None

    Raises:
        TimeoutError: 指定した要素が存在しない場合、または座標クリック対象の要素情報取得に失敗した場合。
        KeyboardInterrupt: ユーザー中断（Ctrl+C）。

    Examples:
        >>> clickAction("ログイン")
        テキスト一致で最初に見つかった「ログイン」ボタンをクリック。

        >>> clickAction("//button[@id='submit']")
        XPath一致の要素をクリック。

    Params:
        - p.click_method (int): クリック方法を指定。
            - 0: 通常のclick()
            - 1: force=Trueでclick()
            - 2: JavaScriptで el.click()
            - 3: hoverしてからclick()
            - 4: 座標クリック（中央座標をクリック）
    """
    global page
    
    element = getElement(page, query)
    if element is None:
        raise TimeoutError(f"指定した要素が見つかりませんでした: {query}")
    
    method = getParam('p.click_method', 0)
    if   method == 0:
        element.click(timeout=5)
    elif method == 1:
        element.click(force=True)
    elif method == 2:
        element.evaluate("el => el.click()")
    elif method == 3:
        # hoverしてからclick
        element.hover()
        time.sleep(1)
        element.click(timeout=5)
    elif method == 4:
        # 座標クリック
        box = element.bounding_box()
        if box is None:
            raise TimeoutError("座標取得できませんでした")
        page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    else:
        raise TimeoutError('p.click_methodが不正です')

@instrumented()
@retryCounter(breakException=[KeyboardInterrupt, TimeoutError])
def doubleClickAction(query):
    """Playwrightで要素をダブルクリックする汎用アクション。

    Args:
        query (str): 検索クエリを指定。

    Returns:
        None

    Raises:
        TimeoutError: 要素が見つからない場合。
        KeyboardInterrupt: ユーザー中断（Ctrl+C）。

    Params:
        - p.dblclick_method (int): ダブルクリック方法を指定。
            - 0: 通常のdblclick()
            - 1: force=Trueでdblclick()
            - 2: JavaScriptでdispatchEvent()
            - 3: hoverしてからdblclick()
            - 4: 座標クリック（中央座標をクリック）
    """
    global page

    element = getElement(page, query)
    if element is None:
        raise TimeoutError(f"指定した要素が見つかりませんでした: {query}")
    method  = getParam('p.double_click_method', 0)
    if   method == 0:
        element.dblclick(timeout=5)
    elif method == 1:
        element.dblclick(force=True)
    elif method == 2:
        element.evaluate("""el => {
            el.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));
        }""")
    elif method == 3:
        element.hover()
        time.sleep(1)
        element.dblclick(timeout=5)
    elif method == 4:
        # 座標ダブルクリック
        box = element.bounding_box()
        if box is None:
            raise TimeoutError("座標取得できませんでした")
        page.mouse.dblclick(
            box['x'] + box['width'] / 2,
            box['y'] + box['height'] / 2
        )
    else:
        raise TimeoutError('p.dblclick_methodが不正です')


@instrumented()
@retryCounter(breakException=[KeyboardInterrupt, TimeoutError])
def rightClickAction(query):
    """Playwrightで要素を右クリックする汎用アクション。

    Args:
        query (str): 検索クエリを指定。

    Returns:
        None

    Raises:
        TimeoutError: 指定した要素が存在しない場合、または座標取得失敗時。
        KeyboardInterrupt: ユーザー中断（Ctrl+C）。

    Params:
        - p.right_click_method (int): 右クリック方法を指定。
            - 0: 通常のclick(button="right")
            - 1: force=Trueでclick(button="right")
            - 2: JavaScriptで右クリックイベント(dispatchEvent)
            - 3: hoverしてからclick(button="right")
            - 4: 座標で右クリック
    """
    global page
    
    element = getElement(page, query)
    if element is None:
        raise TimeoutError(f"指定した要素が見つかりませんでした: {query}")
    method = getParam('p.right_click_method', 0)

    if method == 0:
        element.click(button="right", timeout=5)
    elif method == 1:
        element.click(button="right", force=True)
    elif method == 2:
        element.evaluate("""
            el => {
                const event = new MouseEvent('contextmenu', { bubbles: true, cancelable: true, button: 2 });
                el.dispatchEvent(event);
            }
        """)
    elif method == 3:
        element.hover()
        time.sleep(1)
        element.click(button="right", timeout=5)
    elif method == 4:
        box = element.bounding_box()
        if box is None:
            raise TimeoutError("座標取得できませんでした")
        page.mouse.click(
            box['x'] + box['width'] / 2,
            box['y'] + box['height'] / 2,
            button="right"
        )
    else:
        raise TimeoutError('p.right_click_methodが不正です')


@instrumented()
@retryCounter(breakException=[KeyboardInterrupt, TimeoutError])
def inputAction(query_text):
    global page
    query, text = sepSplit(query_text)
    element = getElement(page, query)
    if element is None:
        raise TimeoutError(f"指定した要素が見つかりませんでした: {query}")
    element.fill(text)


@instrumented()
@retryCounter(breakException=[KeyboardInterrupt, TimeoutError])
def selectAction(query_search):
    global page
    query, search = sepSplit(query_search)
    element = getElement(page, query)
    if element is None:
        raise TimeoutError(f"指定した要素が見つかりませんでした: {query}")
    
    # まず一致する <option> を探す（value か innerText）
    options = element.query_selector_all('option')
    for option in options:
        value = option.get_attribute('value')
        text = option.inner_text()
        if search == value or search == text:
            # value が存在する場合は value で選択
            if value is not None:
                element.select_option(value=value)
            else:
                # value がない場合は label（=表示テキスト）で選択
                element.select_option(label=text)
            return
    return False  # 一致するものがなかった


@instrumented()
@retryCounter(breakException=[KeyboardInterrupt, TimeoutError])
def focusAction(query):
    global page
    element = getElement(page, query)
    if element is None:
        raise TimeoutError(f"指定した要素が見つかりませんでした: {query}")
    element.focus()


@instrumented()
@retryCounter(breakException=[KeyboardInterrupt, TimeoutError])
def waitAction(query=None):
    global page
    
    if query is None:
        wait_state = getParam('p.wait_state')
        page.wait_for_load_state(state=wait_state)
        return
        
    element = None
    while element is None:
        element = getElement(page, query)


@instrumented()
@retryCounter(breakException=[KeyboardInterrupt, TimeoutError])
def uploadAction(query_file):
    global page
    query, file_path = sepSplit(query_file)
    element = getElement(page, query)
    if element is None:
        raise TimeoutError(f"指定した要素が見つかりませんでした: {query}")
    
    # ダブルクォーテーション囲みの場合は除去する
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]

    # アップロードを実行
    if element:
        element.set_input_files(file_path)

@instrumented()
def screenshotAction(file_path=None):
    global page
    
    if not file_path:
        file_path = getParam('p.screenshot.default_dir')

    if os.path.isdir(file_path):
        file_name = f"{getParam('p.screenshot.default_name')}"
        file_path = os.path.join(file_path, file_name)
        base, ext = os.path.splitext(file_path)
    else:
        base, ext = os.path.splitext(file_path)
        if not ext:
            ext = '.png'
            file_path = base + ext
            base = file_path[:-len(ext)]

    overwrite = getParam('p.screenshot.overwrite', default_value=False)

    save_path = file_path
    if not overwrite:
        count = 1
        while os.path.exists(save_path):
            save_path = f"{base}_{count}.{ext}"
            count += 1

    scale = getParam('p.screenshot.scale_type')
    page.screenshot(path=save_path, full_page=True, type='png', scale=scale)


@instrumented()
def getAction(query):
    global page
    element = getElement(page, query)
    if element is None:
        raise TimeoutError(f"指定した要素が見つかりませんでした: {query}")
    text = element.inner_text()
    print(text)
    setParam('text', text)


@instrumented()
def existAction(query):
    global page
    element = getElement(page, query, no_retry=True)
    if element:
        return True
    else:
        return False


playwright_key_map = {
    # 修飾キー
    'ctrl'      : 'Control',
    'shift'     : 'Shift',
    'alt'       : 'Alt',
    'cmd'       : 'Meta',
    'win'       : 'Meta',
    'windows'   : 'Meta',

    # 入力・編集キー
    'enter'     : 'Enter',
    'tab'       : 'Tab',
    'space'     : ' ',
    'backspace' : 'Backspace',
    'delete'    : 'Delete',
    'insert'    : 'Insert',

    # ナビゲーションキー
    'up'        : 'ArrowUp',
    'down'      : 'ArrowDown',
    'left'      : 'ArrowLeft',
    'right'     : 'ArrowRight',
    'home'      : 'Home',
    'end'       : 'End',
    'page_up'   : 'PageUp',
    'page_down' : 'PageDown',

    # ロックキー（Playwrightでは多くがサポート外ですが、必要に応じて追加）
    'caps_lock'     : 'CapsLock',
    'num_lock'      : 'NumLock',
    'scroll_lock'   : 'ScrollLock',

    # ファンクションキー
    'f1'        : 'F1',
    'f2'        : 'F2',
    'f3'        : 'F3',
    'f4'        : 'F4',
    'f5'        : 'F5',
    'f6'        : 'F6',
    'f7'        : 'F7',
    'f8'        : 'F8',
    'f9'        : 'F9',
    'f10'       : 'F10',
    'f11'       : 'F11',
    'f12'       : 'F12',
    'f13'       : 'F13',
    'f14'       : 'F14',
    'f15'       : 'F15',
    'f16'       : 'F16',
    'f17'       : 'F17',
    'f18'       : 'F18',
    'f19'       : 'F19',
    'f20'       : 'F20',

    # システム・その他キー
    'esc'           : 'Escape',
    'pause'         : 'Pause',
    'print_screen'  : 'PrintScreen',  # 一部環境では未サポート
    'menu'          : 'ContextMenu',  # 一部環境では未サポート
}

@instrumented()
def keyAction(keys):
    global page
    key_list = keys.lower().split('+')
    converted_keys = [
        playwright_key_map.get(k, k.upper() if len(k) == 1 else k.title())
        for k in key_list
    ]
    combo = '+'.join(converted_keys)
    page.keyboard.press(combo)


@instrumented()
def stopBrowser():
    global p
    auto_close = getParam('p.browser.auto_close', True)
    if not auto_close:
        print(f"auto_close=Falseのため待機")
        input('Enter...>')
    
    if p:
        print("Stopping browser...", end=' ')
        try:
            p.stop()
            print('[OK]')
        except:
            print('[NG]')


action_list = {
    'open' : openAction,
    'goto' : gotoAction,
    'tab'  : tabAction,
    'click': clickAction,
    'input': inputAction,
    'select': selectAction,
    'focus': focusAction,
    'wait': waitAction,
    'upload': uploadAction,
    'screenshot': screenshotAction,
    'get' : getAction,
    'exist': existAction,
    'key': keyAction,
    'doubleClick': doubleClickAction,
    'rightClick': rightClickAction,
}