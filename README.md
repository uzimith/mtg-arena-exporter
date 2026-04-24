# mtg-arena-exporter

MTG Arena のコレクションを [mtga-tracker-daemon](https://github.com/frcaton/mtga-tracker-daemon) と [Scryfall](https://scryfall.com/) のバルクデータから突き合わせ、CSV として書き出すスクリプトです。おまけで 2 色土地サイクル（スロー／ショック／チェック／ファスト／ペインなど）の所持状況を HTML レポートとして出力できます。

## 必要なもの

- Python 3.10+（標準ライブラリのみ、外部依存なし）
- Windows または Linux（[mtga-tracker-daemon](https://github.com/frcaton/mtga-tracker-daemon) の公式ビルドが提供されている環境）
- MTG Arena を起動してログインし、Collection 画面を一度開いていること（デーモンがコレクションを取得するのに必要）

`--daemon` が localhost を指している場合、mtga-tracker-daemon の最新リリースを GitHub からダウンロードして自動で起動します（バイナリは `--cache` ディレクトリ配下にキャッシュされ、2 回目以降は再利用します）。既に起動済みのデーモンがあればそれを利用します。

## 使い方

```sh
python mtga_export.py
```

初回実行時は Scryfall の `default_cards` バルクデータ（数百 MB）を `~/.cache/mtga-export/` にダウンロードします。2 回目以降は `updated_at` が変わるまでキャッシュを再利用します。

### オプション

| フラグ | デフォルト | 説明 |
| --- | --- | --- |
| `--daemon` | `http://localhost:6842` | mtga-tracker-daemon のベース URL |
| `--out` | `mtga_collection.csv` | CSV の出力先 |
| `--cache` | `~/.cache/mtga-export` | Scryfall バルクデータおよびデーモンバイナリのキャッシュ先 |
| `--html` | （なし） | 指定すると 2 色土地の所持状況を HTML レポートとして出力 |
| `--no-auto-daemon` | （無効） | mtga-tracker-daemon の自動ダウンロード・起動を無効化（既存プロセス前提） |
| `--daemon-update` | （無効） | キャッシュを無視して mtga-tracker-daemon の最新リリースを取り直す |

### 例

```sh
# CSV に加えて土地レポートも出力
python mtga_export.py --html lands.html

# 別ポートで動いているデーモンを指定
python mtga_export.py --daemon http://localhost:7000
```

## 出力

### CSV

以下の列を持つ UTF-8 CSV が出力されます。

`Count, Name, Set Code, Set Name, Collector Number, Rarity, Scryfall ID`

### HTML レポート（`--html` 指定時）

スローランド／ショックランド／チェックランド／ファストランド／ペインランド などの 2 色土地サイクルごとに、10 組（友好色 5 + 対抗色 5）の所持枚数を一覧表示します。

## 備考

- Scryfall の `arena_id` と突き合わせできなかったカード（Alchemy や再調整カードなど）は実行末尾に件数・サンプルが表示されます。CSV には含まれません。
- Scryfall へのリクエストには [API ポリシー](https://scryfall.com/docs/api)に従い `User-Agent` と `Accept` ヘッダを付与しています。
