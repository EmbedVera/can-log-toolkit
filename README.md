# CAN Log Toolkit

Small, transparent utilities for inspecting CAN log timing before you reach for a full analysis suite.

This repository is maintained by **EmbedVera** and intentionally starts with deterministic, easy-to-audit tooling. It is not an AI debugger and it is not a CANoe replacement.

## What works today

The first utility, `canlog_stats.py`, reads a documented subset of Vector-style classic CAN `.asc` data-frame lines and reports:

- frame count and message count;
- per-ID first / last timestamp;
- min / median / mean / max cycle interval;
- timing intervals that deviate from the median by a configurable ratio.

It has **no runtime dependencies** beyond Python 3.10+.

## Quick start

```bash
python canlog_stats.py samples/timing_anomaly.asc
```

Save JSON output:

```bash
python canlog_stats.py samples/timing_anomaly.asc --output result.json
```

Use a stricter timing threshold:

```bash
python canlog_stats.py samples/timing_anomaly.asc --anomaly-ratio 0.10
```

Run the test:

```bash
python -m unittest discover -s tests -v
```

## Example

The included sample contains a CAN ID whose normal interval is `0.500 s`, with two suspicious intervals around one event:

```text
0.500 s
0.500 s
0.250 s  <- shortened
0.750 s  <- delayed recovery
0.500 s
```

The tool reports the two deviations with their timestamps instead of guessing a root cause.

## Supported ASC subset

Current parser target:

```text
<timestamp> <channel> <CAN-ID> <Rx|Tx> d <DLC> <data bytes...>
```

Example:

```text
1.250000 1 123 Rx d 8 01 00 00 00 00 00 00 00
```

This is deliberately narrow in the first public version. Real-world ASC files contain more record types and format variations. If a line is not recognized, it is skipped rather than interpreted heuristically.

## Roadmap

Near-term additions are expected to stay deterministic and testable:

- broader ASC format coverage;
- DBC decoding;
- signal transition summaries;
- missing / delayed frame checks;
- CSV output;
- small reproducible examples.

The higher-level investigation system — hypotheses, evidence linking, engineering context, review, and investigation reporting — belongs to [EmbedVera](https://embedvera.com/), not this repository.

## Reproducible debugging cases

Synthetic and redistributable CAN debugging cases are being collected separately in [EmbedVera/can-debug-benchmark](https://github.com/EmbedVera/can-debug-benchmark).

The goal is to make timing and evidence claims reproducible instead of publishing screenshots that cannot be verified.

## Design principles

1. **Deterministic before generative** — if timing can be calculated, calculate it.
2. **Evidence before conclusion** — report the timestamp and interval that support a finding.
3. **Unknown is acceptable** — a timing anomaly is not automatically a root cause.
4. **Small tools, clear scope** — this repository should remain useful without becoming another full CAN platform.

## 中文说明

这是 EmbedVera 维护的公开 CAN 日志小工具仓库。第一版只做可验证的确定性分析：从 `.asc` 中统计报文周期并定位明显的时序偏差，不尝试用模型猜测根因。

完整的工程问题调查、假设验证、证据链和报告能力由 [EmbedVera](https://embedvera.com/) 承担。

## License

A public open-source license has not been selected yet. A license will be added before the first tagged release.
