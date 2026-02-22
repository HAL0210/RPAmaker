from system.commonDefine import *

def getConnectString(server):
    if not hasParam(f'{server}'):
        raise
    
    ip = getParam(f'{server}.ip')
    us = getParam(f'{server}.user')
    ps = encode_url_component(getParam(f'{server}.pass'))
    connect_str = f'{us}:{ps}@{ip}'
    
    return connect_str


@instrumented()
def uploadAction(server_local_remote):
    server, local, remote = sepSplit(server_local_remote, split=3)
    
    
    

@instrumented()
def downloadAction(server_remote_local):
    server, remote, local = sepSplit(server_remote_local, split=3)
    
    connect_str = getConnectString(server)
    
    winscp_path = getParam('app_path.winscp')
    
    from defaultActions import execAction
    execAction(f'{winscp_path},/command,"open sftp://{connect_str}/-hostkey=*","get {remote} {local}","exit"')


action_list = {
    'upload', uploadAction,
    'download', downloadAction,
}