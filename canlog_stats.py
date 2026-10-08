#!/usr/bin/env python3
"""Small, dependency-free timing statistics tool for Vector-style ASC CAN logs.

This intentionally supports a narrow, documented subset of classic CAN data-frame
lines. It is designed as a transparent engineering utility, not a replacement for
full CAN tooling.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ASC_DATA_FRAME = re.compile(
    r"^\s*(?P<timestamp>\d+(?:\.\d+)?)\s+"
    r"(?P<channel>\d+)\s+"
    r"(?P<can_id>[0-9A-Fa-f]+)(?P<extended>x)?\s+"
    r"(?P<direction>Rx|Tx)\s+"
    r"d\s+(?P<dlc>\d+)"
    r"(?:\s+(?P<data>(?:[0-9A-Fa-f]{2}(?:\s+|$))*))?"
)


@dataclass(frozen=True)
class Frame:
    timestamp: float
    channel: int
    can_id: int
    extended: bool
    direction: str
    dlc: int
    data: tuple[int, ...]


def parse_asc_lines(lines: Iterable[str]) -> list[Frame]:
    frames: list[Frame] = []
    for line in lines:
        match = ASC_DATA_FRAME.match(line)
        if not match:
            continue
        raw_data = (match.group("data") or "").split()
        dlc = int(match.group("dlc"))
        data = tuple(int(byte, 16) for byte in raw_data[:dlc])
        frames.append(
            Frame(
                timestamp=float(match.group("timestamp")),
                channel=int(match.group("channel")),
                can_id=int(match.group("can_id"), 16),
                extended=bool(match.group("extended")),
                direction=match.group("direction"),
                dlc=dlc,
                data=data,
            )
        )
    return frames


def analyze_frames(frames: list[Frame], anomaly_ratio: float = 0.25) -> dict:
    grouped: dict[tuple[int, int, bool], list[Frame]] = defaultdict(list)
    for frame in frames:
        grouped[(frame.channel, frame.can_id, frame.extended)].append(frame)

    messages = []
    for (channel, can_id, extended), group in sorted(grouped.items()):
        group.sort(key=lambda item: item.timestamp)
        intervals = [
            round(group[i].timestamp - group[i - 1].timestamp, 9)
            for i in range(1, len(group))
        ]
        item = {
            "channel": channel,
            "can_id": f"0x{can_id:X}" + ("x" if extended else ""),
            "count": len(group),
            "first_timestamp_s": group[0].timestamp,
            "last_timestamp_s": group[-1].timestamp,
            "dlc_values": sorted({frame.dlc for frame in group}),
            "cycle": None,
        }
        if intervals:
            median = statistics.median(intervals)
            threshold = abs(median) * anomaly_ratio
            anomalies = []
            for idx, interval in enumerate(intervals, start=1):
                if abs(interval - median) > threshold:
                    anomalies.append(
                        {
                            "timestamp_s": group[idx].timestamp,
                            "interval_s": interval,
                            "previous_timestamp_s": group[idx - 1].timestamp,
                        }
                    )
            item["cycle"] = {
                "min_s": min(intervals),
                "median_s": median,
                "mean_s": statistics.mean(intervals),
                "max_s": max(intervals),
                "anomaly_ratio": anomaly_ratio,
                "anomalies": anomalies,
            }
        messages.append(item)

    return {
        "frame_count": len(frames),
        "message_count": len(messages),
        "messages": messages,
    }


def analyze_file(path: Path, anomaly_ratio: float = 0.25) -> dict:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        frames = parse_asc_lines(handle)
    return analyze_frames(frames, anomaly_ratio=anomaly_ratio)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect message timing in a Vector-style ASC CAN log."
    )
    parser.add_argument("asc", type=Path, help="Path to an ASC log")
    parser.add_argument(
        "--anomaly-ratio",
        type=float,
        default=0.25,
        help="Flag intervals that differ from the median by more than this ratio (default: 0.25)",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    if args.anomaly_ratio < 0:
        parser.error("--anomaly-ratio must be >= 0")

    result = analyze_file(args.asc, anomaly_ratio=args.anomaly_ratio)
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
