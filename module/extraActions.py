'''特殊な動作をさせるために用意
'''
from system.commonDefine import *
import subprocess

loadParams('mod\extra.yaml')
logger = getMyLogger(__name__)

@instrumented()
def getSSIDAction():
    """現在接続中のWi-Fi SSIDを取得し、パラメータ'SSID'に設定する。

    説明:
        Windowsの`netsh wlan show interfaces`コマンドを使用して、
        現在接続しているWi-FiネットワークのSSIDを取得します。
        取得したSSIDは`setParam('SSID', ssid)`で保存されます。

    Args:
        なし

    Returns:
        str: 取得したSSID名。

    Raises:
        StopIteration: 'SSID'を含む行が見つからなかった場合。

    Examples:
        >>> getSSIDAction()
        'MyHomeWiFi'

    Params:
        - ssid_decode (str): コマンド出力をデコードする際に使用する文字コード（例: 'utf-8', 'cp932'など）。

    Note:
        - Wi-Fi接続がない場合や、SSIDが非表示設定されている場合はエラーになる可能性があります。
    """
    command_output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'])
    output_str = command_output.decode(getParam('ssid_decode'))
    ssid_line = next(line for line in output_str.split('\n') if 'SSID' in line)
    ssid = ssid_line.split(':')[1].strip()
    setParam('SSID', ssid)
    return ssid
    

@instrumented()
def getVPNAction():
    vpncli_path = getParam('cisco_anyConnect_path')
    try:
        result = subprocess.run(
            [vpncli_path, "stats"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if "Server Address" in line:
                vpn_address = line.split(":", 1)[1].strip()
                print(f'VPN: {vpn_address}')
                if vpn_address == 'Not Available':
                    setParam('VPN', '')
                    return ''
                else:
                    setParam('VPN', vpn_address)
                    return vpn_address
    except Exception as e:
        print("Error:", e)
    return None


action_list = {
    'SSID'  : getSSIDAction,
    'VPN'   : getVPNAction,
}