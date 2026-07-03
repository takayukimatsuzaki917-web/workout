"""react-native-body-highlighter の bodyFront.ts / bodyBack.ts から
筋肉ごとのSVGパスを抽出し、アプリ用の muscles.json に変換する。

出力形式: {"front": {slug: [path, ...]}, "back": {slug: [path, ...]}}
（left/right/common の区別は描画に不要なので、slug単位で全パスをまとめる）
"""
import json
import re
from pathlib import Path

# このスクリプトは web/vendor/ に置かれている前提（リポジトリ内で再現可能）
VENDOR = Path(__file__).resolve().parent
OUT = VENDOR.parent / "data" / "muscles.json"

# パス文字列（"M..." で始まる十分長い引用符文字列）を拾う正規表現
PATH_RE = re.compile(r'"([Mm][^"]{15,})"')
SLUG_RE = re.compile(r'slug:\s*"([^"]+)"')


def parse(ts_path: Path) -> dict[str, list[str]]:
    text = ts_path.read_text(encoding="utf-8")
    # slug位置で分割して、各slugブロック内のパス文字列を集める
    slugs = list(SLUG_RE.finditer(text))
    result: dict[str, list[str]] = {}
    for i, m in enumerate(slugs):
        slug = m.group(1)
        start = m.end()
        end = slugs[i + 1].start() if i + 1 < len(slugs) else len(text)
        block = text[start:end]
        paths = PATH_RE.findall(block)
        result[slug] = paths
    return result


front = parse(VENDOR / "bodyFront.ts")
back = parse(VENDOR / "bodyBack.ts")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"front": front, "back": back}, ensure_ascii=False), encoding="utf-8")

print("front slugs:", {k: len(v) for k, v in front.items()})
print("back slugs:", {k: len(v) for k, v in back.items()})
print("wrote", OUT)
