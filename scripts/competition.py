"""Create a per-competition workspace and download its Kaggle data."""

import argparse
import re
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
COMPETITIONS = ROOT / "competitions"
PROJECT_TEMPLATE = ROOT / "templates" / "tabular" / "pyproject.toml.template"
SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def competition_slug(value: str) -> str:
    if not SLUG_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "Use the competition URL slug, for example 'titanic'."
        )
    return value


def create_workspace(slug: str) -> Path:
    directory = COMPETITIONS / slug
    for name in ("data/raw", "notebooks", "src", "outputs", "submissions"):
        (directory / name).mkdir(parents=True, exist_ok=True)

    pyproject = directory / "pyproject.toml"
    if not pyproject.exists():
        pyproject.write_text(
            PROJECT_TEMPLATE.read_text(encoding="utf-8").replace("__SLUG__", slug),
            encoding="utf-8",
        )

    python_version = directory / ".python-version"
    if not python_version.exists():
        python_version.write_text(
            (ROOT / ".python-version").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    readme = directory / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {slug}\n\n"
            f"コンテスト: https://www.kaggle.com/competitions/{slug}\n\n"
            "このディレクトリ全体は Git 管理対象外です。\n\n"
            "このディレクトリで `uv sync` を実行すると、`pyproject.toml` の依存関係が\n"
            "コンテスト専用の `.venv/` にインストールされます。\n\n"
            "- `data/raw/`: 取得したデータ\n"
            "- `notebooks/`: 分析用ノートブック\n"
            "- `src/`: 再利用するコード\n"
            "- `outputs/`: 学習済みモデルなど\n"
            "- `submissions/`: 提出ファイル\n",
            encoding="utf-8",
        )
    return directory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new", help="create a competition workspace")
    new.add_argument("slug", type=competition_slug)
    download = commands.add_parser("download", help="download and extract competition data")
    download.add_argument("slug", type=competition_slug)
    download.add_argument("--force", action="store_true", help="download again")
    args = parser.parse_args()

    directory = create_workspace(args.slug)
    if args.command == "new":
        print(f"Created {directory}")
        print(f"Run 'uv sync' in {directory} to install its dependencies.")
        return 0

    load_dotenv(ROOT / ".env", override=False)
    kaggle = shutil.which("kaggle")
    if kaggle is None:
        parser.error("Kaggle CLI was not found. Run this with 'uv run'.")
    command = [
        kaggle,
        "competitions",
        "download",
        args.slug,
        "--path",
        str(directory / "data" / "raw"),
        "--unzip",
    ]
    if args.force:
        command.append("--force")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
