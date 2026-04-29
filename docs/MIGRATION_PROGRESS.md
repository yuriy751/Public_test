# PyQt6 Migration Progress

## Estimated completion
Current estimated migration completion: **~58%**.

## Estimation method
Weighted block estimate:
- UI framework migration and new window architecture: 20%
- Gallery/folder workflow and project model: 10%
- ROI/Boundaries/Intensity/Parameters/Mu_t workflow logic: 35%
- Exports and persistence: 15%
- Validation, tests, parity against legacy app: 20%

Current completion by block:
- UI framework migration and new window architecture: 75%
- Gallery/folder workflow and project model: 60%
- ROI/Boundaries/Intensity/Parameters/Mu_t workflow logic: 58%
- Exports and persistence: 55%
- Validation, tests, parity against legacy app: 5%

Weighted total: **~58%**.

## Implemented
- OriginPro-like 3-pane studio layout and workbook tabs.
- Gallery creation (`Gallery_{i}`) and folder creation (`Folder_{i}`), gallery rename/switch.
- Real boundaries pipeline bridge to legacy boundary detector.
- Intensity and boundary/thickness summary calculation.
- Export to JSON and CSV.
- Mu_t refractive-index decision branch (manual vs auto source policy).

## Remaining high-priority items
1. True ROI editing on canvas (interactive boundary drawing/selection).
2. Full Parameters calculation algorithms (2-column/3-column branch parity).
3. Full Mu_t numerical pipeline beyond refractive-index source selection.
4. Multi-gallery processing queue and background worker threads.
5. Regression tests against legacy outputs on golden datasets.
