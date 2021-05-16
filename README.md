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

2. remoteの標準出力をlocalへ転送
    server:
    printを書き換えるアプローチを採用。printに引数が定義されている場合、上手く動作しない。
    別のアプローチを取る必要あり？


### Issue
1. ファイルの読み込みがremote基準になる？
