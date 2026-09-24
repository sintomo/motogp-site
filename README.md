# MotoGP大全（motogp-site）

WGP（1949年〜）から現在までのMotoGPを、シーズン・ライダー・チーム・メーカー単位でまとめる個人サイト。
データはExcelで編集するCSV、ページはPythonスクリプトで自動作成、公開はGitHub Pages。

---

## 1. 仕組み

```
data/*.csv（Excelで編集） ─┐
content/*.html（文章ページ）├─→ build.py ─→ docs/（完成したサイト）─→ GitHub Pages で公開
templates/base.html（共通枠）│
static/（CSS・JS）         ─┘
```

- 1か所のデータから、シーズン・ライダー・チーム・メーカーの各ページを自動で作成し、相互にリンク
- `docs/` は毎回作り直すので **手で編集しない**

## 2. フォルダー構成

```
motogp-site/
├─ build.py           サイト作成スクリプト（データチェック込み）
├─ build.bat          ダブルクリックでサイト作成
├─ check.bat          ダブルクリックでデータチェックのみ
├─ README.md          この説明書
├─ data/              ★普段編集するのはここ（Excel）
├─ content/           文章ページ（規則・技術・時代史など）
├─ templates/base.html  全ページ共通の枠（ヘッダー・メニュー・フッター）
├─ static/            CSS・JS（docs/assets/ にコピーされる）
└─ docs/              完成したサイト（自動作成・GitHub Pagesの公開対象）
```

## 3. 初期設定（最初の1回だけ）

### 3-1. Python
1. https://www.python.org/downloads/ から最新版をインストール
2. インストール画面で **「Add python.exe to PATH」にチェック**
3. `build.bat` をダブルクリック → 「完了: ○ページ」と出ればOK
   ※追加ライブラリは不要（標準機能のみ）

### 3-2. GitHub Pages で公開
1. GitHub アカウント作成（https://github.com/）
2. **GitHub Desktop** をインストール（https://desktop.github.com/）してサインイン
3. GitHub Desktop：File → Add local repository → このフォルダーを選択 →「create a repository」→ Publish repository（公開：Private のチェックを外す）
   ※無料プランの GitHub Pages は公開リポジトリが条件
4. GitHub のリポジトリ画面：Settings → Pages →
   Source：「Deploy from a branch」／Branch：`main`、フォルダー：`/docs` → Save
5. 数分後 `https://<ユーザー名>.github.io/motogp-site/` で公開

## 4. 普段の更新手順

1. `data/` のCSVをExcelで編集 → **「CSV UTF-8（コンマ区切り）」で保存**
2. `build.bat` をダブルクリック
   - エラーがあれば「ファイル名 ○行目：内容」が表示され、サイトは作られない → 直して再実行
3. `docs/index.html` を開いて表示確認
4. GitHub Desktop：変更内容を確認 → Summary に内容を記入（例：2026年最終戦の結果追加）→ Commit → Push
5. 数分後に公開サイトへ反映

## 5. データファイル一覧

| ファイル | 内容 | 主な列 |
|---|---|---|
| riders.csv | ライダー | id, name_ja, name_en, nationality, birth_year, birth_date, birthplace, profile, status, api_id（公式データのID） |
| teams.csv | チーム（スポンサー名が変わっても1チーム） | id, name_ja, country, note, status |
| manufacturers.csv | メーカー | name_ja, id, country, color, note |
| classes.csv | クラス定義 | code, group, order, from, to, note |
| champions.csv | 全クラスの歴代王者 | year, class, rider_id, rider_name, nationality, maker, status |
| seasons.csv | シーズン概要（年×クラス） | year, class, rounds, runner_up_id, constructor_champion, summary, rule_changes, status |
| entries.csv | 参戦記録（年×クラス×ライダー。スポット参戦含む） | year, class, rider_id, team_id（空欄可）, entry_name, maker, machine, number, rank, points, status |
| races.csv | レース（年×クラス×ラウンド） | year, class, round, session（RAC＝決勝／SPR＝スプリント）, gp_code, gp_name_ja, circuit, date, winner_id, status, note, source |
| results.csv | レース結果（1レース×1ライダー） | year, class, round, session, pos, rider_id, number, team, maker, points, result（FIN完走／DNFリタイア／DNS不出走／DSQ失格／EXC除外） |
| timeline.csv | トップの年表 | year, category, text, major |
| class_bars.csv | クラス変遷グラフ | label, from, to, color, text |
| machines.csv | マシン図鑑 | name, class, maker, years, engine, note |
| battles.csv | 名勝負 | year, race, who, note |
| legends.csv | 時代を代表するライダー | name, era, titles, note |
| japanese.csv | 日本人ライダー | name, era, note |
| circuits.csv | サーキット | name, info, note |
| sources.csv | 出典 | title, url, used_for |

### 列のルール
- **id**：半角小文字・数字・ハイフンのみ。ページのURLになる（例：`marc-marquez` → `riders/marc-marquez.html`）。一度決めたら変えない
- **class**：`classes.csv` の code（MotoGP / 500cc / 250cc / Moto2 / 125cc / Moto3 / 350cc / 50cc / 80cc / MotoE）
- **maker**：`manufacturers.csv` の name_ja と同じ表記（ホンダ、ヤマハ、ドゥカティ…）
- **status**：情報の確かさ
  - `確認済`：出典で確認した
  - `記憶`：出典と未照合（ページに「未照合」と表示）
  - `要確認`：不確か（ページに「要確認」と表示）
- **rank**：年間順位（数字）。不明なら空欄
- note / profile 列は HTML 可（例：`<span class="chk">要確認</span>`）

### よくある更新
| やりたいこと | 手順 |
|---|---|
| 新シーズンの参戦者を追加 | entries.csv に1人1行。新顔は先に riders.csv、新チームは teams.csv に追加 |
| 年間順位を入れる | entries.csv の rank に数字 |
| 王者を追加 | champions.csv に1行（rider_id を入れるとライダーページにリンク） |
| シーズン概要を追加 | seasons.csv に1行（年×クラス） |
| 過去シーズンを拡充 | seasons.csv → riders.csv / teams.csv → entries.csv の順で追加 |
| 文章ページを直す | content/ の該当HTML |
| メニューを変える | build.py 冒頭の NAV |

## 6. Excel利用時の注意
- 保存形式は必ず **「CSV UTF-8（コンマ区切り）」**（普通の「CSV」保存でも読めるが、特殊文字が化ける場合あり）
- 1行目（列名）は変更・削除しない
- 年や順位に書式（「2025年」など）を付けない。数字のみ
- セル内のコンマ・改行はExcelが自動処理するのでそのままでOK

## 7. 今後の拡充計画
| 段階 | 範囲 | 状況 |
|---|---|---|
| 0 | 仕組み（データ設計・作成スクリプト・チェック） | 完了 |
| 1 | MotoGP時代（2002〜2026年）最高峰 | シーズン概要25年分・王者は入力済。参戦一覧は2024〜2026年のみ → 2002〜2023年を追加予定 |
| 2 | 1949〜2025年 全クラス 全参戦者・全レース結果 | 入力済（公式リザルト。2001年以前は一部英語版Wikipediaで補完。サイドカーは未収録）。2026年は MotoGP の参戦一覧のみ |
| 3 | 500cc時代（1949〜2001年） | 入力済（段階2に含む） |
| 4 | 中・小排気量の全シーズン、レース単位の結果 | 未着手 |

## 8. 仕組みの修正
- 見た目：`static/css/style.css`（色・フォントは先頭の変数）
- 共通の枠：`templates/base.html`
- ページの構成・集計：`build.py`（シーズン／ライダー／チーム／メーカー各ページの作成処理）
