# tools（公式リザルトの取り込みスクリプト）

Claude が使う取り込み用。普段の更新では使わない。Python標準ライブラリ＋curl＋pdftotext（poppler）が必要。

| 手順 | コマンド | 内容 |
|---|---|---|
| 1 | `python crawl.py 2002 2009` | MotoGP公式リザルトAPIから年間順位・決勝結果・ライダー情報を取得（cache/ に保存） |
| 2 | `python pdfget.py 2002 2009` | 各決勝の公式リザルトPDFを取得してテキスト化（pdf/ に保存） |
| 3 | `python era.py 2002 2009`（2001年以前は `python era2.py 1990 2001`：公式PDFのURL推定＋英語版Wikipediaで補完） | API＋PDFを突き合わせて era_2002_2009.json を作成 |
| 4 | `python merge_era.py 2002 2009` | data/ の races・results・entries・riders・seasons・manufacturers に反映 |

- 新しいライダーの日本語表記は ja_names.py に追加（日本人は確かなもののみ漢字）
- 名前の表記ゆれ（同一人物）は resolve.py の ALIAS に追加。姓＋頭文字が同じだけの別人は自動で統合しない
- 国・グランプリ・メーカーの日本語表記は maps.py
