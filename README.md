# Remote runner

### Motivation
リモートのマシンでローカルにあるpythonファイルを実行したい

### Approach


### Log
1. clientとserverの作成
    client:
    実行するpythonファイルをserverへソケット通信で送信
    server:
    ローカルホストのポート9999にバインド。
    送信されてきた内容をexecで実行。
