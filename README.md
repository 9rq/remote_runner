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

3. printを書き換えるアプローチの限界
    server:
    printの引数を反映させる場合、alt_printの定義にprintを使うことに。
    置き換えが正しくできなくなる？
    書き切ったが正しく動作できない。

4. stdoutの上書き
    server:
    #3から変更を加え、sys.stdoutを書き換えるアプローチを採用。
    printではio.writeが呼ばれるため、writeを持つソケットを作成した。
    動作の確認はできたものの、空行が入ってしまうことがある。
    上手く行くこともあり、おそらくclient側の問題？
    client側で改行しないように設定することで問題を解決

5. RemoteFinderその1
    server:
    ファイル実体のないstrをimportする機能の実装
    impが古くなっていたのでimportlibを採用
    ファイルをローカルから持ってくる機能は未実装

    Reference:
    https://pod.hatenablog.com/entry/2019/07/25/005334


### Issue
1. ファイルの読み込みがremote基準になる？
