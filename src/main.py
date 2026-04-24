"""
kwmaster v7 - 主入口（串起三步 + 断点续跑）

orchestration 模式下，第二步（score）需要 host Claude 写答案，
所以 main.py 不能一把梭，分成两个阶段：

  阶段 A (prepare + prompts):
    python main.py prompts <workspace>
    跑完会落 prompt 文件，提示 host Claude 去答

  阶段 B (collect + rank):
    python main.py rank <workspace>
    要求 cache/score_answers/ 下答案齐了

  其它:
    python main.py status <workspace>     看每步状态
    python main.py prepare <workspace>    单跑第一步
    python main.py all <workspace>        相当于先跑 prompts 再提示
"""
from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

import prepare  # noqa: E402
import score    # noqa: E402
import rank     # noqa: E402


def step_prepare(ws: Path, force: bool = False) -> None:
    out = ws / "cache" / "clusters.csv"
    if out.exists() and not force:
        print(f"[main] prepare: {out} exists, skipping (use --force to rerun)")
        return
    prepare.run(ws)


def step_prompts(ws: Path) -> None:
    import os
    batch = int(os.environ.get("KWMASTER_BATCH", score.DEFAULT_BATCH))
    score.cmd_prompts(ws, batch)


def step_collect_and_rank(ws: Path) -> None:
    score.cmd_collect(ws)
    rank.run(ws)


def cmd_status(ws: Path) -> None:
    print(f"[main] workspace: {ws}")
    clusters = ws / "cache" / "clusters.csv"
    print(f"  prepare:  {'OK' if clusters.exists() else '--'}  {clusters}")

    prompt_dir = ws / "cache" / "score_prompts"
    answer_dir = ws / "cache" / "score_answers"
    if prompt_dir.exists():
        prompts = sorted(prompt_dir.glob("batch_*.md"))
        answers = sorted(answer_dir.glob("batch_*.json")) if answer_dir.exists() else []
        answered = {p.stem for p in answers}
        pending = [p.stem for p in prompts if p.stem not in answered]
        print(f"  prompts:  {len(prompts)} total, {len(answers)} answered, {len(pending)} pending")
    else:
        print("  prompts:  --")

    scored = ws / "cache" / "scored.csv"
    print(f"  collect:  {'OK' if scored.exists() else '--'}  {scored}")

    out_dir = ws / "output"
    expected = ["P0_priority.csv", "P1_priority.csv", "P2_priority.csv", "EXCLUDED.csv"]
    if out_dir.exists():
        present = [f for f in expected if (out_dir / f).exists()]
        print(f"  rank:     {len(present)}/4 CSVs in {out_dir}")
    else:
        print("  rank:     --")


USAGE = """Usage:
  python main.py status   <workspace>
  python main.py prepare  <workspace> [--force]
  python main.py prompts  <workspace>     # prepare + score prompts
  python main.py rank     <workspace>     # score collect + rank
  python main.py all      <workspace>     # prepare + prompts (then wait for host)
"""


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(USAGE, file=sys.stderr)
        return 2
    cmd = argv[1]
    ws = Path(argv[2]).expanduser().resolve()
    force = "--force" in argv[3:]

    if cmd == "status":
        cmd_status(ws)
    elif cmd == "prepare":
        step_prepare(ws, force=force)
    elif cmd == "prompts":
        step_prepare(ws, force=force)
        step_prompts(ws)
        print()
        print("[main] >>> NEXT: host Claude reads cache/score_prompts/batch_NNNN.md")
        print("[main] >>>       and writes answers to cache/score_answers/batch_NNNN.json")
        print(f"[main] >>>       then run: python main.py rank {ws}")
    elif cmd == "rank":
        step_collect_and_rank(ws)
    elif cmd == "all":
        step_prepare(ws, force=force)
        step_prompts(ws)
        print()
        print("[main] all: stages A done. Waiting for host Claude to score.")
        print(f"[main] When score_answers/ is filled, run: python main.py rank {ws}")
    else:
        print(USAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
