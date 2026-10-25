# Kaggle コンテスト用テンプレート

```text
.
├── pyproject.toml       # Kaggle 取得ツール用の依存関係
├── uv.lock              # 取得ツール用の固定バージョン
├── scripts/
│   └── competition.py  # 作成・ダウンロード用コマンド
├── templates/tabular/   # 新規コンテストの初期依存関係
└── competitions/         # 配下はすべて Git 管理対象外
    └── <slug>/
        ├── README.md
        ├── pyproject.toml   # コンテスト専用の依存関係
        ├── .python-version
        ├── uv.lock          # uv sync / uv run で生成
        ├── .venv/           # コンテスト専用の仮想環境
        ├── data/raw/     # ダウンロードしたデータ
        ├── notebooks/
        ├── src/
        ├── outputs/      # 学習済みモデルなど
        └── submissions/  # 提出ファイル
```

## 使い方

rootで下記を実行
`https://www.kaggle.com/competitions/{id}`のid部分を入力する。

```
uv run python scripts/competition.py new {id}
uv run python scripts/competition.py download {id}
```

`new` は NumPy、pandas、scikit-learn、LightGBM を初期依存として
`competitions/<slug>/pyproject.toml` に設定します。パッケージはそのコンテストで
`uv sync` または `uv run` を実行したときにインストールされます。

初期設定
```
cd competitions/{id}
uv sync
```

ライブラリのインストール
```
uv add xgboost
```

初期依存は `templates/tabular/pyproject.toml.template` で変更できます。

