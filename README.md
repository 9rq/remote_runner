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

6. RemoteImporterの分離
    server:
    RemoteImporterをRemoterFinder + StringLoaderに分割

    Reference:
    https://qiita.com/yasuo-ozu/items/7e4ae538e11dd2d589a8

### Issue
1. ファイルの読み込みがremote基準になる？


### Others
PythonのImportシステム
importの処理は、検索と読み込みの2つに分離できる。
#### 手順
1. まずは`sys.modules`からキャッシュを確認し、読み込み済みかを確認する。
2. インポートプロトコルの起動。
3. Finderによる検索
4. `sys.meta_path`のfinderにアクセスしfind\_specする。



Importer = Finder + Loader
importerはモジュールがロードできることがわかると自分自身を返す。
ファインダーはモジュールのインポート関連の情報をカプセル化したもの(module spec)を返します
インポートフック(メタフック`sys.meta_path`、インポートパスフック`sys.path_hook`)
デフォルトのFinderは`sys.meta_path`に含まれる3つ

