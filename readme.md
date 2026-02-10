# CarbonPricingX

CarbonPricingX is a Streamlit decision-support app for carbon pricing and internal carbon strategy.
It helps teams estimate emissions cost exposure, simulate internal carbon fees, evaluate abatement initiatives (MACC + finance), test cap-and-trade outcomes, model offsets, and export reports.

## What this app includes

- Carbon pricing simulator (`$0` to `$250` per tCO2e)
- Scope/department emissions baseline from activity data
- Internal carbon fee simulation by department
- Abatement planner with:
  - MACC ordering (by `cost_per_tonne`)
  - adoption threshold (`carbon_price >= cost_per_tonne`)
  - finance outputs (`ROI`, `NPV`, `IRR`)
- Cap-and-trade simulator (cap, allocations, trading limits, bank balance)
- Offset model (limit %, quality discount, integrity effect)
- Export center (PDF, Excel, JSON)
- Historical run storage and comparison

## UI tabs

- `Dashboard`
- `Carbon Pricing Simulator`
- `Internal Carbon Market`
- `Abatement Strategy Planner`
- `Cap-and-Trade Simulator`
- `Offset Simulator`
- `Export Center`
- `Historical Runs`

## Tech stack

- Python
- Streamlit
- Pandas
- Plotly
- ReportLab
- OpenPyXL
- Pytest

## Project layout

```text
carbonpricingx/
├── app.py
├── pyproject.toml
├── requirements.txt
├── readme.md
├── .streamlit/
│   └── config.toml
├── carbon_pricing_x/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   └── streamlit_app.py
├── data/
│   ├── sample_departments.csv
│   ├── emission_factors.csv
│   ├── abatement_template.csv
│   ├── sample_activities.xlsx
│   └── market/
│       └── sample_allowances.csv
├── modules/
│   ├── emissions_engine.py
│   ├── carbon_pricing.py
│   ├── internal_market.py
│   ├── abatement.py
│   ├── finance.py
│   ├── cap_and_trade.py
│   ├── offset_engine.py
│   ├── excel_parser.py
│   ├── visualization.py
│   ├── export_pdf.py
│   ├── export_excel.py
│   ├── storage.py
│   └── utils.py
└── tests/
```

## Installation and run

### Option 1: direct run

```bash
cd "personal project/carbonpricingx"
pip install -r requirements.txt
streamlit run app.py
```

### Option 2: package + CLI

```bash
cd "personal project/carbonpricingx"
pip install -e .
carbonpricingx run
```

Optional:

```bash
carbonpricingx run --port 8502 --headless
```

## Quick start workflow

1. Launch the app.
2. (Optional) Upload CSV/XLSX in sidebar.
3. Click `Start Analyze Uploaded Data`.
4. Confirm top caption changes to `Active dataset: uploaded:<filename>`.
5. Tune carbon price and scenario controls.
6. Review results in tabs.
7. Export PDF/Excel/JSON and save run history.

## Upload behavior (important)

Upload is a two-step flow by design:

1. Parse upload
2. Apply to active analysis via `Start Analyze Uploaded Data`

Supported payload combinations:

- Activities only
- Abatement only
- Allowances only
- Mixed workbook (activities + abatement + allowances)

If activities are not provided, the app keeps the current activity baseline and still applies uploaded abatement/allowances.

## Input schemas

### Activities (required for emissions baseline)

Columns:

- `department`
- `scope`
- `activity`
- `amount`
- `unit`
- `emission_factor`
- `source`

Validation:

- no missing `department`
- `amount >= 0`
- numeric `amount`
- numeric `emission_factor`

### Abatement initiatives

Required columns:

- `initiative_name`
- `department`
- `target_scope`
- `cost_per_tonne`
- `capex`
- `max_reduction_pct`

Alias supported:

- `reduction_pct` -> mapped to `max_reduction_pct`

### Allowances

Columns:

- `year`
- `allocated_allowances`
- `initial_cap`
- `offset_limit_pct`

### XLSX sheet naming

Preferred names:

- `Activities`
- `Department-mapped data`
- `Abatement initiative list`
- `Allowances`

The parser also auto-detects sheet type from columns if sheet names differ.

## Core formulas

### Carbon pricing

- `adjusted_activity_factor = (1 - elasticity * (price/100)) * (1 - fuel_switching - energy_efficiency)`
- `adjusted_emissions = baseline_emissions * clamp(adjusted_activity_factor, 0, 1)`
- `carbon_cost = adjusted_emissions * price`

### Internal carbon fee

- `fee_cost = dept_emissions * internal_fee_rate`
- `response_multiplier = clamp(1 - response_factor * internal_fee_rate / 100, 0, 1)`
- `adjusted_emissions = dept_emissions * response_multiplier`

### Abatement adoption

- Adopt initiative when `carbon_price >= cost_per_tonne`
- `reduction_tonnes = baseline_segment_emissions * max_reduction_pct`

### Abatement finance

- annual savings and variable cost are converted to initiative cash flows
- `NPV` computed with selected discount rate and horizon
- `IRR` computed by bisection on cash flow sign change

### Cap-and-trade

- `clearing_price = base_price * (demand / supply) * scarcity_factor`
- buy/sell decisions based on deficit/surplus versus owned allowances and trading limit

### Offsets

- `eligible_offsets = total_emissions * offset_limit_pct`
- `effective_offset_cost = offset_price * quality_discount_factor`
- `effective_reduction = eligible_offsets * (integrity_score / 100)`

## Exports and run history

In `Export Center`:

- PDF report
- Excel workbook
- JSON simulation package
- Save run to `runs/run_<timestamp>.json`

In `Historical Runs`:

- load previous summary
- compare two runs (`delta_emissions`, `delta_total_carbon_cost`)

## Testing

Run all tests:

```bash
cd "personal project/carbonpricingx"
python3 -m pytest -q
```

## Troubleshooting

### Upload says “No recognized rows found”

- Ensure at least one valid dataset exists (activities, abatement, or allowances).
- For abatement-only files, include required abatement columns listed above.

### Upload parsed but results still look old

- Click `Start Analyze Uploaded Data` after upload.
- Check top caption for active dataset.

### Dark/unreadable table or button styles

- Restart app after pulling latest changes.
- Hard refresh browser (`Cmd+Shift+R` on macOS).

### Port already in use

Run with a different port:

```bash
carbonpricingx run --port 8502
```

## Notes

- Current emissions baseline uses activity-level `emission_factor` directly.
- `emission_factors` sheet is parsed but not yet used in live factor substitution.
