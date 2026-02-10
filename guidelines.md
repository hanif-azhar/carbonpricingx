CarbonPricingX — Carbon Pricing Simulator & Internal Carbon Market

CarbonPricingX is a modular Streamlit application that models how carbon pricing, carbon taxes, cap-and-trade markets, and internal carbon fees affect company costs, emissions, abatement behavior, and strategic decisions.
The app simulates carbon costs across multiple price scenarios, models departmental fee systems, evaluates abatement options using marginal abatement cost curves (MACC), and includes a full cap-and-trade market engine with allowance trading.
This is a decision-support toolkit designed for:
•	sustainability teams
•	corporate strategy units
•	climate consultants
•	financial analysts
•	policy researchers
 
What the App Does
✔ 1) Carbon Pricing Impact Simulator
•	Run carbon price scenarios from $0 → $250 per tonne
•	Compute cost exposure for:
o	Scope 1 (direct fuel combustion)
o	Scope 2 (electricity purchased)
o	Scope 3 (value-chain segments)
•	Apply elasticity settings for demand & efficiency response
•	Display cost curves, threshold impacts, and breakpoints
 
✔ 2) Internal Carbon Fee System
Simulates a corporate carbon “internal tax” applied per department:
•	manufacturing
•	logistics & shipping
•	retail
•	R&D
•	offices
•	data centers
Outputs:
•	Department cost burden
•	Behavioral response
•	Emissions reductions per department
•	Net-cost vs savings chart
 
✔ 3) Marginal Abatement Cost Curve (MACC) Engine
Evaluate emissions-reduction initiatives with:
•	cost per tonne (USD/tCO2e)
•	reduction potential (%)
•	payback period
•	adoption threshold when carbon price > initiative cost
Auto-build MAC curve & recommended abatement sequence.
 
✔ 4) Cap-and-Trade Market Simulator
Includes a simple but powerful ETS engine:
•	emission cap
•	allowance allocation
•	trading rules
•	offset limits
•	scarcity factor
•	market clearing price calculation
Simulate:
•	buying/selling allowances
•	total compliance cost
•	net position
•	allowance bank balance over time
 
✔ 5) Offset Purchasing Model
Supports:
•	offset price
•	integrity scoring
•	max allowable offset usage (%)
•	discount factor for low-quality offsets
 
✔ 6) Excel Upload for Activity + Emission Data
Supports multi-sheet .xlsx and CSV.
Expected schemas:
•	Activities
•	Emission factors
•	Department-mapped data
•	Abatement initiative list
 
✔ 7) Export Center
Export:
•	PDF report (cost curves, MACC, ETS summary)
•	Excel report (inputs + outputs + charts)
•	JSON simulation pack
 
✔ 8) Historical Run Storage
Saves runs to /runs/run_<timestamp>.json.
 
Technology Stack
•	Python
•	Streamlit
•	Pandas
•	Plotly
•	ReportLab (PDF export)
•	SQLite / JSON
•	pytest
 
Project Structure
carbon_pricing_x/
├── app.py
├── requirements.txt
├── readme.md
├── data/
│   ├── emission_factors.csv
│   ├── sample_activities.xlsx
│   ├── sample_departments.csv
│   ├── abatement_template.csv
│   └── market/
│       └── sample_allowances.csv
├── modules/
│   ├── emissions_engine.py
│   ├── carbon_pricing.py
│   ├── internal_market.py
│   ├── abatement.py
│   ├── cap_and_trade.py
│   ├── offset_engine.py
│   ├── excel_parser.py
│   ├── visualization.py
│   ├── export_pdf.py
│   ├── export_excel.py
│   ├── storage.py
│   └── utils.py
└── tests/
    ├── test_emissions.py
    ├── test_carbon_pricing.py
    ├── test_internal_market.py
    ├── test_abatement.py
    ├── test_cap_and_trade.py
    ├── test_offset.py
    ├── test_excel_parser.py
    └── test_storage.py
 
Input Data Specification
1. Activities (required)
Columns:
•	department
•	scope
•	activity
•	amount
•	unit
•	emission_factor
•	source
Rules:
•	no missing departments
•	no negative activity values
•	EF must be numeric
 
2. Emission Factors (optional)
Columns:
•	scope
•	activity
•	co2_factor
•	ch4_factor
•	n2o_factor
•	region
•	year
 
3. Abatement Initiatives
Columns:
•	initiative_name
•	max_reduction_pct
•	cost_per_tonne
•	capex
•	target_scope
•	department
 
4. Cap-and-Trade Allowances
Columns:
•	year
•	allocated_allowances
•	initial_cap
•	offset_limit_pct
 
Modeling Approach
 
Carbon Cost Equation
For a given scenario carbon price P:
carbon_cost = total_emissions_tonnes * P
Elasticity (activity reduction when price rises):
adjusted_activity = activity * (1 - elasticity * (P / 100))
 
Internal Carbon Fee Allocation
department_fee_cost = dept_emissions * internal_fee_rate
Behavioral change:
new_dept_emissions = dept_emissions * (1 - response_factor * internal_fee_rate/100)
 
Marginal Abatement Cost Curve (MACC)
Initiative is adopted if:
carbon_price >= cost_per_tonne
Total reduction:
reduction = baseline_emissions * max_reduction_pct
Sort initiatives ascending by cost_per_tonne to construct MAC curve.
 
Cap-and-Trade: Market Clearing Price
Core logic:
•	compute supply (allowances)
•	compute demand (emissions)
•	if demand > supply → price ↑
Simplified clearing model:
price = base_price * (demand / supply)
Compliance cost:
if emissions > allowances:
    buy = emissions - allowances
else:
    sell = allowances - emissions
 
Offset Model
eligible_offsets = total_emissions * offset_limit_pct
effective_offset_cost = offset_price * quality_discount_factor
 
Streamlit Tabs
1) Dashboard
•	Total emissions
•	Total carbon cost
•	Recommended carbon price
•	Top 3 departments by exposure
 
2) Carbon Pricing Simulator
Sliders:
•	carbon price
•	elasticity
•	fuel-switching factor
•	energy efficiency factor
Charts:
•	cost curve
•	emissions vs price
 
3) Internal Carbon Market
Tables:
•	department emissions
•	department fee cost
•	adjusted emissions
Charts:
•	fee distribution
•	behavior response
 
4) Abatement Strategy Planner
Charts:
•	MAC curve
•	cumulative reduction
•	ROI timeline
 
5) Cap-and-Trade Simulator
Inputs:
•	annual cap
•	free allocations
•	trading limits
Outputs:
•	clearing price
•	net allowance position
•	compliance cost
 
6) Offset Simulator
•	offset usage
•	quality score impact
•	price sensitivity
 
7) Export Center
•	PDF report
•	Excel model
•	JSON run package
 
8) Historical Runs
Load and compare:
•	emissions
•	cost exposure
•	MAC curves
•	ETS compliance
 
Testing
python3 -m pytest -q
Covers:
•	pricing logic
•	elasticity response
•	MAC curve calculation
•	ETS trading
•	offset behavior
•	Excel parsing
 
Troubleshooting
Carbon cost too high:
Check units (e.g., kg vs tonnes)
ETS price unstable:
Adjust scarcity factor
Adjust initial cap
Offsets not applied:
Ensure offset_limit_pct > 0
 
Next Steps / Extension Ideas
•	multi-region carbon tax comparison
•	carbon leakage model
•	supply chain carbon pass-through
•	regression-based emissions forecasting
•	real-time carbon market price API
 

