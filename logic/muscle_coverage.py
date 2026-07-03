"""筋肉ハイライト分類ロジック。

各種目の `muscle_svg_ids` は「主動筋（メイン）」を先頭、
「協働筋（サブ）」をそれ以降に並べる規約になっている。
この規約に基づき、体図（SVG）で色分け表示するための
分類辞書を組み立てる純粋関数群。
"""

from __future__ import annotations

PRIMARY = "primary"
SECONDARY = "secondary"


def classify_exercise_muscles(exercise_entry: dict) -> dict[str, str]:
    """1種目分の対象筋肉を主動筋(primary)・協働筋(secondary)に分類する。

    引数:
        exercise_entry: build_program()が返す種目1件分の辞書（muscle_svg_idsを含む）
    戻り値:
        {muscle_svg_id: "primary" | "secondary"} の辞書
    """
    muscle_ids = exercise_entry["muscle_svg_ids"]
    if not muscle_ids:
        return {}

    classification = {muscle_ids[0]: PRIMARY}
    for muscle_id in muscle_ids[1:]:
        classification.setdefault(muscle_id, SECONDARY)
    return classification


def aggregate_program_coverage(exercises: list[dict]) -> dict[str, str]:
    """プログラム全種目を横断して、筋肉ごとの分類を集約する（全身カバレッジビュー用）。

    いずれかの種目で主動筋(primary)として扱われていればprimaryを優先する。

    引数:
        exercises: build_program()が返す"exercises"リスト
    戻り値:
        {muscle_svg_id: "primary" | "secondary"} の辞書
    """
    coverage: dict[str, str] = {}
    for exercise_entry in exercises:
        for muscle_id, level in classify_exercise_muscles(exercise_entry).items():
            if coverage.get(muscle_id) == PRIMARY:
                continue
            coverage[muscle_id] = level
    return coverage
