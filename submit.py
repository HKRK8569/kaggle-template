"""Kaggle への提出と提出履歴の確認。"""

import argparse
import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def competition_slug(value: str) -> str:
    if not SLUG_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError("コンペティションの URL 末尾を指定してください。例: titanic")
    return value


def competition_from_path(path: Path) -> str | None:
    try:
        relative = path.resolve().relative_to((ROOT / "competitions").resolve())
    except ValueError:
        return None
    if not relative.parts:
        return None
    slug = relative.parts[0]
    return slug if SLUG_PATTERN.fullmatch(slug) else None


def infer_status_competition() -> str | None:
    slug = competition_from_path(Path.cwd())
    if slug:
        return slug
    directory = ROOT / "competitions"
    if not directory.is_dir():
        return None
    candidates = [item.name for item in directory.iterdir() if item.is_dir() and SLUG_PATTERN.fullmatch(item.name)]
    return candidates[0] if len(candidates) == 1 else None


def validate_titanic_submission(path: Path) -> int:
    test_path = ROOT / "competitions" / "titanic" / "data" / "raw" / "test.csv"
    if not test_path.is_file():
        raise ValueError(f"検証用の test.csv が見つかりません: {test_path}")
    with test_path.open(encoding="utf-8-sig", newline="") as file:
        expected = [row["PassengerId"] for row in csv.DictReader(file)]
    if not expected or len(expected) != len(set(expected)):
        raise ValueError("test.csv の PassengerId が空、または重複しています。")
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["PassengerId", "Survived"]:
            raise ValueError("提出 CSV の列は PassengerId,Survived の順にしてください。")
        rows = list(reader)
    if any(None in row or row["Survived"] not in {"0", "1"} for row in rows):
        raise ValueError("各行の Survived は 0 または 1 にしてください。")
    ids = [row["PassengerId"] for row in rows]
    if len(ids) != len(expected) or len(ids) != len(set(ids)) or set(ids) != set(expected):
        raise ValueError("PassengerId は test.csv と同じ乗客を重複なく含めてください。")
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kaggle に CSV を提出し、スコアや提出履歴を確認します。")
    commands = parser.add_subparsers(dest="action", required=True)
    submit = commands.add_parser("submit", help="提出し、採点を待つ")
    submit.add_argument("competition", nargs="?", type=competition_slug, help="コンペティションの URL 末尾（省略時は CSV から推定）")
    submit.add_argument("file", type=Path, help="提出する CSV ファイル")
    submit.add_argument("-m", "--message", help="提出メモ（省略時はファイル名）")
    submit.add_argument("--wait", type=int, default=120, metavar="SECONDS", help="採点待ちの秒数（既定: 120）")
    submit.add_argument("--no-wait", action="store_true", help="採点完了を待たずに終了")
    status = commands.add_parser("status", help="提出履歴とスコアを表示")
    status.add_argument("competition", nargs="?", type=competition_slug, help="コンペティションの URL 末尾（省略可）")
    args = parser.parse_args(argv)

    if args.action == "submit":
        if args.wait <= 0:
            parser.error("--wait は正の秒数を指定してください。")
        path = args.file.expanduser().resolve()
        if not path.is_file() or path.suffix.lower() != ".csv":
            parser.error(f"提出する CSV ファイルが見つかりません: {path}")
        args.competition = args.competition or competition_from_path(path) or competition_from_path(Path.cwd())
        if not args.competition:
            parser.error("コンペティションを特定できません。CSV の前に ID を指定してください。")
        print(f"コンペティション: {args.competition}", flush=True)
        if args.competition == "titanic":
            try:
                count = validate_titanic_submission(path)
            except (ValueError, KeyError, OSError, csv.Error) as exc:
                parser.error(f"提出 CSV を確認してください: {exc}")
            print(f"Titanic の提出 CSV を確認しました: {count} 行", flush=True)
    else:
        args.competition = args.competition or infer_status_competition()
        if not args.competition:
            parser.error("コンペティションを特定できません。status の後に ID を指定してください。")
        print(f"コンペティション: {args.competition}", flush=True)

    load_dotenv(ROOT / ".env", override=False)
    kaggle = shutil.which("kaggle")
    if kaggle is None:
        parser.error("Kaggle CLI が見つかりません。ルートで uv run python submit.py を実行してください。")

    if args.action == "status":
        command = [kaggle, "competitions", "submissions", args.competition, "--page-size", "10"]
    else:
        command = [kaggle, "competitions", "submit", args.competition, "-f", str(path), "-m", args.message or path.stem]
        if not args.no_wait:
            command += ["--wait", str(args.wait), "--poll-interval", "5"]

    try:
        result = subprocess.run(command, check=False)
    except OSError as exc:
        print(f"Kaggle CLI を実行できません: {exc}", file=sys.stderr)
        return 1
    if args.action == "submit":
        print(
            f"提出状況の確認: uv run python submit.py status {args.competition}",
            file=sys.stderr if result.returncode else sys.stdout,
        )
        if result.returncode:
            print("提出済みで採点待ちの可能性もあります。再提出前に提出履歴を確認してください。", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
