# HumanStudyBench

A benchmark framework for evaluating LLM agents on classic human behavioral studies.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

> A realistic, sustainable, and systematic benchmark for evaluating AI agents' ability to reproduce published human studies.

HumanStudyBench curates classic and contemporary peer‑reviewed studies with full experimental specifications (designs, participant profiles, measurement protocols, and reported results). Agents run under realistic constraints and are scored against literature‑reported outcomes.

## Features

- 🧪 Curated studies across domains (e.g., Asch conformity)
- 👤 LLM‑as‑Participant: agents act as human participants
- 📊 Built‑in validation against ground truth results
- 💾 Caching: run once, re‑evaluate for free
- 🔧 Extensible study/config system and metrics
- 📚 Documentation and examples included

## Quick start

Run an experiment with caching, then evaluate cached results without new API calls.

```bash
# Run Asch (study_001) with caching
python run_full_benchmark.py \
  --real-llm \
  --model mistralai/mistral-nemo \
  --studies study_001 \
  --n-participants 5 \
  --num-workers 3 \
  --use-cache

# Evaluate latest cached result (no API calls)
python evaluate_results.py --latest

# Or evaluate all cached runs
python evaluate_results.py --all
```

## Usage

```bash
python run_full_benchmark.py [OPTIONS]
```

Key options:

| Option | Description | Default |
|---|---|---|
| `--real-llm` | Use real LLM (vs. mock agent) | Off |
| `--model MODEL` | LLM model id (OpenRouter supported) | mistralai/mistral-nemo |
| `--studies STUDY [STUDY...]` | Studies to run | All |
| `--n-participants N` | Number of participants | Study default |
| `--num-workers N` | Parallel workers | 5 |
| `--use-cache` | Enable caching | Off |
| `--cache-dir DIR` | Cache directory | results/cache |
| `--random-seed SEED` | Seed for reproducibility | 42 |

## Cache system

- On `--use-cache`, results are saved and reused by signature (study, model, participants, seed).
- Re‑evaluate cached data with `evaluate_results.py` without making new API calls.

Filename format:

```
{study_id}__{model_slug}__n{participants}__seed{seed}.json
```

Example: `study_001__mistralai_mistral-nemo__n123__seed42.json`

## OpenRouter support

HumanStudyBench supports [OpenRouter](https://openrouter.ai/) with `mistralai/mistral-nemo` as a sensible default. Switch models by changing `--model`.

Examples:

```bash
python run_full_benchmark.py --real-llm --model anthropic/claude-3-sonnet --use-cache
python run_full_benchmark.py --real-llm --model meta-llama/llama-3-70b-instruct --use-cache
```

See `docs/openrouter_guide.md` for details.

## Project structure

```
HS_bench/
├── data/                      # Study registry, schemas, and studies
│   └── studies/
│       └── study_001/         # Asch conformity (1952)
├── src/
│   ├── agents/                # LLM participant agents & prompt builder
│   ├── core/                  # Benchmark orchestration & study base
│   ├── evaluation/            # Scoring and metrics
│   └── studies/               # Study-specific configs
├── results/
│   └── cache/                 # Cached runs
├── run_full_benchmark.py      # Experiment runner
├── evaluate_results.py        # Standalone evaluator (no API calls)
└── README.md
```

## Current studies

### Study 001 — Asch Conformity Experiment (1952)

- Domain: Social Psychology
- Design: Neutral vs. critical trials, with confederate pressure
- Key finding: ~37% conformity when the group is unanimously wrong
- Validation: Conformity rate range, control accuracy, majority conformity, significance vs control, distribution similarity

Full description: `data/studies/study_001/STUDY_INFO.md`

## Evaluation & pass criteria

Study‑level grades:

| Overall Score | Grade | Status |
|---|---|---|
| 100% | Perfect | ✅ Pass |
| ≥ 85% | High Quality | ✅ Pass |
| ≥ 70% | Pass | ✅ Pass |
| < 70% | Fail | ❌ Fail |

Some tests are marked as critical; failing any critical test fails the study regardless of score.

Benchmark‑level pass requires BOTH: average score ≥ 60% and pass rate ≥ 50%.

## Troubleshooting

- Timeouts or rate limits: lower `--num-workers`, or try a faster/cheaper model.
- Cache issues: omit `--use-cache` for a fresh run, or remove specific files in `results/cache`.

## Documentation

- Getting started: `docs/getting_started.md`
- Agent guide: `docs/llm_participant_agent_guide.md`
- Prompt builder: `docs/prompt_builder_guide.md`
- OpenRouter: `docs/openrouter_guide.md`
- Benchmark overview: `docs/benchmark_overview.md`
- Evaluation metrics: `docs/evaluation_metrics.md`

## Contributing

Issues and PRs are welcome. See `docs/paper_curation_guide.md` for adding new studies.

## Citation

```bibtex
@misc{humanstudybench2025,
  title={HumanStudyBench: A Benchmark for Evaluating AI Agents on Human Study Replication},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/HS_bench}
}
```

