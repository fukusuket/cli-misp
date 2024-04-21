# cli-misp
CLIからMISPイベントを作成するツール
### Input
以下プロンプトに従い入力。**(*)** は必須項目。それ以外の項目で不明(or不要)な場合は、未入力+EnterでOK。
<img alt="Logo" src="demo.gif">

### Output
上記実行後にMISPにイベントが作成される。
<img alt="misp1" src="misp1.png" width="70%">
<img alt="misp2" src="misp2.png" width="80%">

## 事前準備
#### Python
1. [Python 3.12.3](https://www.python.org/downloads) をインストール
2. CLIで、`python3 -V` できることを確認
3. CLIで、`pip3 -v` できることを確認
4. `pip3 install --upgrade pip` で`pip3`を最新化する

#### Git
1. Gitをインストール
2. CLIで、`git -v` できることを確認

## インストール
1. `git clone https://github.com/fukusuket/cli-misp.git`
2. `cd cli-misp`
3. `pip3 install -r requirements.txt`
4. MISPのURLを`cli-misp.py`の11行目にセットする 
5. MISPのAPIキーを`cli-misp.py`の12行目にセットする
6. `python3 cli-misp.py`でエラーにならないことを確認(URL/APIキー間違いの場合はエラー終了する)

## 使い方
`python3 cli-misp.py` を実行し、順次質問に入力する。

## ツールが付与するコンテキスト
### Taxonomy
- https://www.circl.lu/doc/misp-taxonomies/#_tlp_2
- https://www.circl.lu/doc/misp-taxonomies/#_course_of_action
- https://www.circl.lu/doc/misp-taxonomies/#_estimative_language
- https://www.circl.lu/doc/misp-taxonomies/#_workflow

### Galaxy
- 付与しない（手動で付与する）