# Remote runner

## Motivation
リモートのマシンでローカルにあるpythonファイルを実行したい。<br>
標準ライブラリのみを利用して、Pure Pythonな実装。

****

## Approach
|remote                      | local                        |
|----------------------------|------------------------------|
|importで見つからない        |                              |
|localへリクエスト           |                              |
|                            | リクエストの受理             |
|                            | importの実行                 |
|                            | finderで実体ファイルを探す   |
|                            | specとsourceを転送           |
|specとsourceの受け取り      |                              |
|loaderの実行                |                              |

****

## Log
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

6. RemoteImporterの分離
    server:
    RemoteImporterをRemoterFinder + StringLoaderに分割

    Reference:
    https://qiita.com/yasuo-ozu/items/7e4ae538e11dd2d589a8

7. socket通信の強化
    それぞれMySocketに機能を実装
    receive:
    ストリーム通信であるため、送信データの区切りを示す必要あり。
    - 固定長を送る
    - 区切り文字を設定
    - メッセージ長をヘッダーとして追加
    公式リファレンスには上記の手段が挙げられている。
    今回は区切り文字としてcrlf(\\r\\n)を採用
    send:
    sendを実行したからといって全てが送信されているとは限らない。
    戻り値を確認して残りを送信する。
    最後にcrlfをつけるのを忘れないように。

    Reference:
    [ソケットプログラミング HOWTO](https://docs.python.org/ja/3/howto/sockets.html#using-a-socket)

8. RemoteFinderその2
    RemoteFinderを`sys.meta_path`に追加。
    importに失敗した時にRemoteFinder.find_specを実行し、importリクエストを送信する。
    受け取りの実装は先送り。

9. importリクエストへの対応
    client:
    importリクエストを受け取り、find_specを実行する。
    module.originからsourceファイルを特定し、sourceとspecをserverへ転送する。
    server:
    受け取ったsourceを元にloaderを作成、上書きする。
    実行はpythonに任せる。

****

## Issue
1. ファイルの読み込みがremote基準になる
2.  ~~`from ... import ...`に対応しない？~~
3. 区切り文字がソケット通信の中身に入っていると区切られてしまう。
4. `*.so`ファイルが読み込めない

****

## Others
### PythonのImportシステム
import を実行すると、`__import__`が呼ばれる。
主要箇所は`_find_and_load_unlocked`
[cpython/Lib/importlib/\_bootstrap.py](https://github.com/python/cpython/blob/79d1c2e6c9d1bc1cf41ec3041801ca1a2b9a995b/Lib/importlib/_bootstrap.py)
#### 流れ
大雑把に要約すると以下のような処理を行う。

1. 親モジュールを確認し、必要に応じて再帰的に読み込む
2. `sys.meta_path`にあるFinderに対して`find_spec`を呼び出し、specを取得する
3. specに付属したLoaderを元に`create_module`により、moduleを生成した後に`exec_module`を実行し、moduleを読み込む

import機構を書き換えたい場合、FinderとLoaderを作成した上で、`sys.meta_path`に追加(or 上書き)するのが楽。

### socket通信
ソケット通信はストリーム通信であるため、データの切れ目が定義されていない。
対話的に通信を行うためには、データの区切り方を決める必要がある。
固定長のメッセージにする、区切り文字を指定する、メッセージ長を先行して送信する、といった方法が存在する。
pythonの公式ドキュメントでは、3つ目が推奨されていた。
今回は実装が楽であるため区切り文字を指定している。
しかしながら、メッセージ内に区切り文字が存在してしまうと正しくメッセージが解釈できなくなるのでよくないかもしれない。
