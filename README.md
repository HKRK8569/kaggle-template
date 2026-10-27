# Kaggle コンテスト用テンプレート

```text
.
├── pyproject.toml       # 全コンテスト共通の依存関係
├── uv.lock              # 共通環境の固定バージョン
├── .venv/               # 共通の仮想環境
├── .vscode/             # 共通環境を選ぶ VS Code 設定
├── submit.py            # 提出と提出履歴の確認
├── scripts/
│   └── competition.py   # 作成・ダウンロード用コマンド
└── competitions/        # 配下はすべて Git 管理対象外
    └── <slug>/
        ├── README.md
        ├── .vscode/      # 共有環境への参照
        ├── data/raw/     # ダウンロードしたデータ
        ├── notebooks/
        ├── src/
        ├── outputs/      # 学習済みモデルなど
        └── submissions/  # 提出ファイル
```

## 使い方

VS Code ではリポジトリのルートまたはコンテストのディレクトリを開けます。
Python と Jupyter の拡張機能を使い、ノートブックのカーネルには
ルートの `.venv` を選びます。

最初にルートで共通環境を同期します。

```
uv sync
```

コンテストの URL が `https://www.kaggle.com/competitions/{id}` の場合、
ルートから次を実行します。

```
uv run python scripts/competition.py new {id}
uv run python scripts/competition.py download {id}
```

追加のPythonライブラリが必要になったときは、ルートの `pyproject.toml` に追加します。

## 提出とスコアの確認

提出コマンド

```
uv run python submit.py submit competitions/titanic/submissions/all_remove_cabin_embarked_fare_rf.csv
```
提出結果確認コマンド

全部
```
uv run python submit.py status
```

id指定
```
uv run python submit.py status {id}
```
