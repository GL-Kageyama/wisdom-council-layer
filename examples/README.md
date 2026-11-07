**Language:** [English](README.md) | [日本語](README-ja.md) | [中文](README-zh.md)

# Examples — Samples by Genre

A collection of samples demonstrating the **generate → evaluate → recreate** loop for each genre.

## Placement guide

When adding a sample, decide the location in this order:

1. **Does it belong to a specific genre or domain?** → `<genre-domain>/`
2. **Is it a one-off output, old version, or backup?** → `_archive/`

- One sample per folder. Keep `input.md` + `report-v1.json` + `report-v2.json` + `report.md`.
- Name the folder after the genre (`creative-film`, `business-startup`).
- If the number of genres grows, group them into `creative/` `business/` `science/` `culture/` and move the folders under them.
- After adding, add one row to the table above.

## Folder Structure

| Folder | Genre | Classification transition (v1 → v2) |
|----------|---------|----------------------|
| `creative-poem/` | Poetry | discovery_target → current_success |
| `creative-poem-sea/` | Poetry (the sea · "Borrowed Words") | discovery_target → innovation (v1–v10) |
| `creative-poem-sea-desk/` | Poetry (the sea · "Sea Desk") | discovery_target (v1) |
| `music-lyrics/` | Popular-song lyrics ("Phone Call After the Rain") | trend_object → innovation (v1–v5) |
| `creative-film/` | Film project | discovery_target → innovation |
| `creative-watercolor/` | Image-generation prompt (watercolor) | discovery_target → innovation |
| `creative-photography/` | Image-generation prompt (photography) | discovery_target → innovation |
| `business-startup/` | Business | trend_object → current_success |
| `scientific-hypothesis/` | Scientific hypothesis | discovery_target → innovation |
| `cultural-philosophy/` | Philosophical essay | low_signal → discovery_target |
| `digital-oss/` | OSS software | trend_object → current_success |
| `architecture-house/` | Private residence design (architecture) | discovery_target → innovation |
| `digital-elevate-draft-engine/` | AI-generation engine (code · full council) | discovery_target (v1) |

Each genre folder contains:
- `input.md` — the content to be evaluated (v1・v2)
- `report-v1.json` — initial evaluation (strict scores)
- `report-v2.json` — re-evaluation after revision (demonstrates loop improvement)
- `report.md` — Markdown rendering of v2 (readable in GitHub / VSCode preview)

## Usage

**Read an evaluation (as Markdown):**
```bash
python ../utils/render_report.py --format md business-startup/report-v2.json
```

**Also show the individual report of every evaluator:**
```bash
python ../utils/render_report.py --individuals business-startup/report-v2.json
```

**Compare loop improvement:**
```bash
python ../utils/compare_reports.py business-startup/report-v1.json business-startup/report-v2.json
```

**Validate all samples:**
```bash
for f in */report-*.json; do python3 ../utils/validate_output.py "$f"; done
```

## Individual Evaluation Reports (individual_reports)

Each report's `individual_reports` holds the **raw data of every convened evaluator** (`weaknesses`・`improvement_suggestions`・`narrative`). This is **the input that creation skills read as material for re-creation**.

- **`business-startup/`** is the **canonical form**, fully implementing the individual reports of all 6 evaluators (verifiable with `--individuals`).
- The samples for other genres are **summarized for readability**. An actual council saves every convened evaluator.
