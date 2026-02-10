from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.abatement import evaluate_abatement
from modules.cap_and_trade import CapTradeConfig, simulate_cap_and_trade
from modules.carbon_pricing import CarbonPricingConfig, recommend_carbon_price, run_price_scenarios
from modules.emissions_engine import calculate_emissions
from modules.excel_parser import parse_uploaded_file
from modules.export_excel import build_excel_report
from modules.export_pdf import build_pdf_report
from modules.internal_market import InternalFeeConfig, simulate_internal_fee
from modules.offset_engine import simulate_offsets
from modules.storage import compare_runs, list_runs, load_run, save_run
from modules.visualization import (
    behavior_response,
    cumulative_reduction,
    emissions_vs_price,
    fee_distribution,
    macc_curve,
    npv_by_initiative,
    pricing_cost_curve,
    roi_timeline,
    style_figure,
)

DATA_DIR = PROJECT_ROOT / "data"
RUNS_DIR = PROJECT_ROOT / "runs"


def _safe_read_csv(path: Path, fallback_columns: list[str]) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=fallback_columns)


def _init_state() -> None:
    defaults = {
        "activities_df": _safe_read_csv(
            DATA_DIR / "sample_departments.csv",
            ["department", "scope", "activity", "amount", "unit", "emission_factor", "source"],
        ),
        "abatement_df": _safe_read_csv(
            DATA_DIR / "abatement_template.csv",
            ["initiative_name", "max_reduction_pct", "cost_per_tonne", "capex", "target_scope", "department"],
        ),
        "allowances_df": _safe_read_csv(
            DATA_DIR / "market" / "sample_allowances.csv",
            ["year", "allocated_allowances", "initial_cap", "offset_limit_pct"],
        ),
        "last_saved_run": "",
        "pending_upload": None,
        "pending_upload_sig": "",
        "active_data_source": "sample_data",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

        html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
            font-family: "Space Grotesk", "Avenir Next", "Segoe UI", sans-serif;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 20% 0%, rgba(16, 185, 129, 0.14), transparent 45%),
                radial-gradient(circle at 80% 10%, rgba(14, 165, 233, 0.14), transparent 40%),
                linear-gradient(180deg, #f3fbf6 0%, #f5f8fb 60%, #eef7fb 100%);
            color: #10231d;
        }

        [data-testid="stHeader"] {
            background: rgba(0, 0, 0, 0);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #123226 0%, #1f4d41 45%, #224f68 100%);
            color: #e9fff7;
        }

        [data-testid="stSidebar"] * {
            color: #e9fff7;
        }

        section.main, section.main * {
            color: #10231d;
        }

        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5,
        [data-testid="stCaptionContainer"] {
            color: #10231d !important;
        }

        [data-baseweb="tab-list"] {
            gap: 0.35rem;
            margin-bottom: 0.55rem;
        }

        [data-baseweb="tab"] {
            color: #27463d !important;
            background: rgba(255, 255, 255, 0.66) !important;
            border: 1px solid rgba(16, 35, 29, 0.12);
            border-radius: 9px 9px 0 0;
            padding: 0.3rem 0.65rem;
        }

        [aria-selected="true"][data-baseweb="tab"] {
            color: #0f766e !important;
            font-weight: 700 !important;
            border-bottom: 2px solid #0f766e !important;
            background: rgba(239, 250, 246, 0.9) !important;
        }

        [role="tablist"] button p {
            color: inherit !important;
        }

        .hero-wrap {
            padding: 1rem 1.2rem;
            border-radius: 18px;
            background: linear-gradient(120deg, #104f3f, #0f766e 55%, #0284c7);
            box-shadow: 0 14px 28px rgba(2, 132, 199, 0.18);
            color: #e8fff8;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            margin: 0;
            font-size: 1.75rem;
            letter-spacing: 0.02em;
            font-weight: 700;
        }

        .hero-subtitle {
            margin-top: 0.35rem;
            opacity: 0.9;
            font-size: 0.95rem;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.7rem;
            margin: 0.4rem 0 0.9rem 0;
        }

        .kpi-card {
            background: linear-gradient(160deg, #fdfefe, #ecf7f1);
            border: 1px solid rgba(16, 185, 129, 0.25);
            border-radius: 14px;
            padding: 0.8rem 0.85rem;
            box-shadow: 0 8px 20px rgba(16, 185, 129, 0.08);
        }

        .kpi-label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #1f2937;
            opacity: 0.85;
        }

        .kpi-value {
            font-size: 1.16rem;
            font-weight: 700;
            color: #0f172a;
            margin-top: 0.25rem;
            font-family: "IBM Plex Mono", "SFMono-Regular", Menlo, monospace;
        }

        [data-testid="stMetric"] {
            background: linear-gradient(160deg, #fdfefe, #ecf7f1);
            border: 1px solid rgba(16, 185, 129, 0.22);
            border-radius: 12px;
            padding: 0.4rem 0.55rem;
        }

        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"] {
            color: #10231d !important;
        }

        [data-testid="stDataFrame"] {
            background: rgba(255, 255, 255, 0.74);
            border: 1px solid rgba(16, 35, 29, 0.12);
            border-radius: 12px;
            overflow: hidden;
            --gdg-bg-cell: #f8fdfb !important;
            --gdg-bg-cell-medium: #eef8f4 !important;
            --gdg-bg-header: #dff2ea !important;
            --gdg-bg-header-hovered: #d1ebdf !important;
            --gdg-bg-bubble: #f8fdfb !important;
            --gdg-bg-bubble-selected: #e7f4ee !important;
            --gdg-text-dark: #10231d !important;
            --gdg-text-medium: #2f4a42 !important;
            --gdg-text-light: #557069 !important;
            --gdg-border-color: rgba(16, 35, 29, 0.12) !important;
            --gdg-horizontal-border-color: rgba(16, 35, 29, 0.09) !important;
            --gdg-accent-color: #0f766e !important;
            --gdg-font-family: "Space Grotesk", "Avenir Next", "Segoe UI", sans-serif !important;
        }

        [data-testid="stDataFrame"] [role="grid"],
        [data-testid="stDataFrame"] .glide-data-grid,
        [data-testid="stDataFrame"] .gdg-container {
            background: #f8fdfb !important;
            color: #10231d !important;
        }

        [data-testid="stDataFrame"] canvas {
            background-color: #f8fdfb !important;
        }

        .stButton > button,
        [data-testid="stDownloadButton"] > button,
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-primary"],
        button[kind="secondary"],
        button[kind="primary"] {
            background: linear-gradient(135deg, #0f766e, #0284c7) !important;
            color: #f4fffb !important;
            border: 1px solid rgba(15, 118, 110, 0.36) !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            box-shadow: 0 8px 18px rgba(2, 132, 199, 0.2);
        }

        .stButton > button:hover,
        [data-testid="stDownloadButton"] > button:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[kind="secondary"]:hover,
        button[kind="primary"]:hover {
            background: linear-gradient(135deg, #0d6f68, #0369a1) !important;
            color: #ffffff !important;
            border-color: rgba(3, 105, 161, 0.5) !important;
        }

        .stButton > button:focus,
        [data-testid="stDownloadButton"] > button:focus {
            outline: 2px solid rgba(14, 165, 233, 0.55) !important;
            outline-offset: 1px;
        }

        .stButton > button p,
        [data-testid="stDownloadButton"] > button p,
        .stButton > button span,
        [data-testid="stDownloadButton"] > button span {
            color: #f4fffb !important;
        }

        [data-testid="stJson"] {
            border: 1px solid rgba(16, 35, 29, 0.12);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.74);
        }

        @media (max-width: 1024px) {
            .kpi-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero-wrap">
          <h1 class="hero-title">CarbonPricingX</h1>
          <div class="hero-subtitle">Carbon pricing, internal markets, abatement finance, ETS simulation, offsets, and reporting in one workspace.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _kpi_cards(items: list[tuple[str, str]]) -> None:
    card_html = ["<div class='kpi-grid'>"]
    for label, value in items:
        card_html.append(
            "<div class='kpi-card'>"
            f"<div class='kpi-label'>{label}</div>"
            f"<div class='kpi-value'>{value}</div>"
            "</div>"
        )
    card_html.append("</div>")
    st.markdown("".join(card_html), unsafe_allow_html=True)


def _to_json_records(df: pd.DataFrame) -> list[dict]:
    return df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else []


def _styled_table(df: pd.DataFrame):
    return df.style.set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("background-color", "#dff2ea"),
                    ("color", "#10231d"),
                    ("font-weight", "600"),
                    ("border", "1px solid #bddfd1"),
                ],
            },
            {
                "selector": "td",
                "props": [
                    ("background-color", "#f8fdfb"),
                    ("color", "#10231d"),
                    ("border", "1px solid #d7ece3"),
                ],
            },
        ]
    )


def run_app() -> None:
    st.set_page_config(page_title="CarbonPricingX", page_icon="🌿", layout="wide")
    _inject_styles()
    _render_hero()
    _init_state()
    st.caption(f"Active dataset: `{st.session_state.active_data_source}`")

    st.sidebar.header("Data Inputs")
    uploaded = st.sidebar.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"])
    if uploaded is not None:
        upload_sig = f"{uploaded.name}:{getattr(uploaded, 'size', 0)}"
        if st.session_state.pending_upload_sig != upload_sig:
            try:
                parsed = parse_uploaded_file(uploaded)
            except Exception as exc:
                st.sidebar.error(f"Upload parsing failed: {exc}")
            else:
                st.session_state.pending_upload = {
                    "name": uploaded.name,
                    "activities": parsed.activities,
                    "departments": parsed.departments,
                    "abatement": parsed.abatement,
                    "allowances": parsed.allowances,
                }
                st.session_state.pending_upload_sig = upload_sig
                st.sidebar.success("Input file parsed. Click Start Analyze Uploaded Data.")

    pending_upload = st.session_state.pending_upload
    if pending_upload is not None:
        candidate_activities = pending_upload["activities"]
        if candidate_activities.empty:
            candidate_activities = pending_upload["departments"]
        candidate_abatement = pending_upload["abatement"]
        candidate_allowances = pending_upload["allowances"]

        st.sidebar.caption(
            "Parsed rows -> "
            f"activities: {len(candidate_activities)}, "
            f"abatement: {len(candidate_abatement)}, "
            f"allowances: {len(candidate_allowances)}"
        )

        if st.sidebar.button("Start Analyze Uploaded Data", type="primary"):
            has_any_payload = (not candidate_activities.empty) or (not candidate_abatement.empty) or (not candidate_allowances.empty)
            if not has_any_payload:
                st.sidebar.error(
                    "No recognized rows found. Add at least one valid sheet: activities, abatement, or allowances."
                )
            else:
                if not candidate_activities.empty:
                    st.session_state.activities_df = candidate_activities.copy()
                if not candidate_abatement.empty:
                    st.session_state.abatement_df = candidate_abatement.copy()
                if not candidate_allowances.empty:
                    st.session_state.allowances_df = candidate_allowances.copy()

                st.session_state.active_data_source = f"uploaded:{pending_upload['name']}"
                if candidate_activities.empty:
                    st.sidebar.warning(
                        "No activity sheet in upload. Reusing current activity baseline and applying uploaded abatement/allowances."
                    )
                else:
                    st.sidebar.success("Uploaded data is now active and analyzed.")
                st.rerun()

    if st.sidebar.button("Reset to sample data"):
        for key in [
            "activities_df",
            "abatement_df",
            "allowances_df",
            "pending_upload",
            "pending_upload_sig",
            "active_data_source",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        _init_state()

    st.sidebar.header("Abatement Finance")
    discount_rate_pct = st.sidebar.slider("Discount rate (%)", 0.0, 20.0, 8.0, 0.5)
    analysis_years = st.sidebar.slider("Analysis horizon (years)", 3, 25, 10)
    annual_savings_growth_pct = st.sidebar.slider("Annual savings growth (%)", -5.0, 10.0, 0.0, 0.5)

    activities_df = st.session_state.activities_df
    abatement_df = st.session_state.abatement_df
    allowances_df = st.session_state.allowances_df

    try:
        emissions_result = calculate_emissions(activities_df)
    except Exception as exc:
        st.error(f"Input validation error: {exc}")
        st.stop()

    baseline_total = emissions_result["total_emissions"]
    baseline_dept = emissions_result["by_department"]
    baseline_detailed = emissions_result["detailed"]

    (
        tab_dashboard,
        tab_pricing,
        tab_internal,
        tab_abatement,
        tab_captrade,
        tab_offsets,
        tab_export,
        tab_history,
    ) = st.tabs(
        [
            "Dashboard",
            "Carbon Pricing Simulator",
            "Internal Carbon Market",
            "Abatement Strategy Planner",
            "Cap-and-Trade Simulator",
            "Offset Simulator",
            "Export Center",
            "Historical Runs",
        ]
    )

    pricing_col1, pricing_col2, pricing_col3, pricing_col4 = st.columns(4)
    selected_carbon_price = pricing_col1.slider("Carbon price (USD/tCO2e)", 0, 250, 75)
    elasticity = pricing_col2.slider("Elasticity", 0.0, 1.0, 0.10, 0.01)
    fuel_switching_factor = pricing_col3.slider("Fuel-switching factor", 0.0, 0.5, 0.05, 0.01)
    energy_efficiency_factor = pricing_col4.slider("Energy efficiency factor", 0.0, 0.5, 0.05, 0.01)

    pricing_config = CarbonPricingConfig(
        elasticity=elasticity,
        fuel_switching_factor=fuel_switching_factor,
        energy_efficiency_factor=energy_efficiency_factor,
    )
    pricing_df = run_price_scenarios(baseline_total, range(0, 251), pricing_config)
    selected_pricing = pricing_df.loc[pricing_df["carbon_price"] == float(selected_carbon_price)]
    selected_cost = (
        float(selected_pricing["carbon_cost"].iloc[0]) if not selected_pricing.empty else baseline_total * selected_carbon_price
    )

    abatement_result = evaluate_abatement(
        abatement_df,
        baseline_detailed,
        selected_carbon_price,
        discount_rate=discount_rate_pct / 100.0,
        analysis_years=analysis_years,
        annual_savings_growth=annual_savings_growth_pct / 100.0,
    )
    macc_df = abatement_result["macc"]
    recommended_price = recommend_carbon_price(macc_df)

    with tab_dashboard:
        st.subheader("Dashboard")
        top3 = baseline_dept.head(3).copy()
        top3["cost_exposure"] = top3["emissions_tonnes"] * selected_carbon_price

        _kpi_cards(
            [
                ("Total emissions", f"{baseline_total:,.2f} tCO2e"),
                ("Total carbon cost", f"${selected_cost:,.2f}"),
                ("Recommended price", f"${recommended_price:,.2f}/tCO2e"),
                (
                    "Portfolio NPV",
                    f"${abatement_result['total_npv']:,.2f}",
                ),
            ]
        )

        t1, t2 = st.columns([1.2, 1])
        with t1:
            st.markdown("Top 3 departments by exposure")
            st.table(_styled_table(top3))
        with t2:
            dept_chart = px.bar(
                top3,
                x="department",
                y="cost_exposure",
                title="Department Exposure",
                color="cost_exposure",
                color_continuous_scale="Tealgrn",
            )
            st.plotly_chart(style_figure(dept_chart), use_container_width=True)

        st.markdown("Baseline emissions by scope")
        st.dataframe(_styled_table(emissions_result["by_scope"]), use_container_width=True)

    with tab_pricing:
        st.subheader("Carbon Pricing Simulator")
        st.plotly_chart(pricing_cost_curve(pricing_df), use_container_width=True)
        st.plotly_chart(emissions_vs_price(pricing_df), use_container_width=True)
        st.dataframe(_styled_table(pricing_df), use_container_width=True)

    with tab_internal:
        st.subheader("Internal Carbon Fee System")
        fee_col1, fee_col2 = st.columns(2)
        internal_fee_rate = fee_col1.slider("Internal fee rate (USD/tCO2e)", 0, 300, 60)
        response_factor = fee_col2.slider("Response factor", 0.0, 1.0, 0.15, 0.01)

        internal_result = simulate_internal_fee(
            baseline_dept,
            InternalFeeConfig(internal_fee_rate=internal_fee_rate, response_factor=response_factor),
        )
        m1, m2 = st.columns(2)
        m1.metric("Total fee burden", f"${internal_result['total_fee_cost']:,.2f}")
        m2.metric("Total emissions reduction", f"{internal_result['total_reduction']:,.2f} tCO2e")
        st.dataframe(_styled_table(internal_result["table"]), use_container_width=True)
        st.plotly_chart(fee_distribution(internal_result["table"]), use_container_width=True)
        st.plotly_chart(behavior_response(internal_result["table"]), use_container_width=True)

    with tab_abatement:
        st.subheader("Marginal Abatement Cost Curve (MACC)")
        st.caption("Initiatives are adopted when carbon_price >= cost_per_tonne.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total adopted reduction", f"{abatement_result['total_reduction']:,.2f} tCO2e")
        m2.metric("Total abatement cost", f"${abatement_result['total_cost']:,.2f}")
        m3.metric("Portfolio NPV", f"${abatement_result['total_npv']:,.2f}")
        portfolio_irr = abatement_result.get("portfolio_irr")
        m4.metric("Portfolio IRR", f"{portfolio_irr * 100:,.2f}%" if portfolio_irr is not None else "N/A")

        st.dataframe(_styled_table(macc_df), use_container_width=True)
        if not macc_df.empty:
            st.plotly_chart(macc_curve(macc_df), use_container_width=True)
            st.plotly_chart(cumulative_reduction(macc_df), use_container_width=True)
            st.plotly_chart(roi_timeline(macc_df), use_container_width=True)
            st.plotly_chart(npv_by_initiative(macc_df), use_container_width=True)

    with tab_captrade:
        st.subheader("Cap-and-Trade Market Simulator")
        defaults = allowances_df.iloc[0].to_dict() if not allowances_df.empty else {}

        cap_col1, cap_col2, cap_col3, cap_col4 = st.columns(4)
        annual_cap = cap_col1.number_input(
            "Annual cap",
            min_value=0.0,
            value=float(defaults.get("initial_cap", baseline_total * 0.9)),
        )
        free_allocations = cap_col2.number_input(
            "Free allocations",
            min_value=0.0,
            value=float(defaults.get("allocated_allowances", baseline_total * 0.7)),
        )
        trading_limit_pct = cap_col3.slider("Trading limit pct", 0.0, 1.5, 1.0, 0.05)
        scarcity_factor = cap_col4.slider("Scarcity factor", 0.1, 3.0, 1.0, 0.1)

        cap_col5, cap_col6, cap_col7 = st.columns(3)
        offset_limit_pct = cap_col5.slider(
            "Offset limit pct",
            0.0,
            1.0,
            float(defaults.get("offset_limit_pct", 0.15)),
            0.01,
        )
        base_price = cap_col6.number_input("Base market price", min_value=1.0, value=45.0)
        bank_balance = cap_col7.number_input("Allowance bank balance", min_value=0.0, value=0.0)

        captrade_result = simulate_cap_and_trade(
            emissions_tonnes=baseline_total,
            config=CapTradeConfig(
                annual_cap=annual_cap,
                free_allocations=free_allocations,
                trading_limit_pct=trading_limit_pct,
                offset_limit_pct=offset_limit_pct,
                base_price=base_price,
                scarcity_factor=scarcity_factor,
                bank_balance=bank_balance,
            ),
            offsets_used=0.0,
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Clearing price", f"${captrade_result['clearing_price']:,.2f}")
        c2.metric("Compliance cost", f"${captrade_result['compliance_cost']:,.2f}")
        c3.metric("Net position", f"{captrade_result['net_position']:,.2f} allowances")
        c4.metric("Bank balance", f"{captrade_result['bank_balance']:,.2f}")
        st.json(captrade_result)

    with tab_offsets:
        st.subheader("Offset Purchasing Model")
        off_col1, off_col2, off_col3, off_col4 = st.columns(4)
        offset_price = off_col1.number_input("Offset price", min_value=0.0, value=18.0)
        integrity_score = off_col2.slider("Integrity score", 0.0, 100.0, 80.0, 1.0)
        quality_discount_factor = off_col3.slider("Quality discount factor", 0.0, 1.5, 0.9, 0.05)
        offset_limit_pct_for_offsets = off_col4.slider("Max offset usage pct", 0.0, 1.0, 0.15, 0.01)

        offset_result = simulate_offsets(
            total_emissions=baseline_total,
            offset_price=offset_price,
            integrity_score=integrity_score,
            offset_limit_pct=offset_limit_pct_for_offsets,
            quality_discount_factor=quality_discount_factor,
        )

        o1, o2, o3 = st.columns(3)
        o1.metric("Eligible offsets", f"{offset_result['eligible_offsets']:,.2f} tCO2e")
        o2.metric("Total offset cost", f"${offset_result['total_offset_cost']:,.2f}")
        o3.metric("Residual emissions", f"{offset_result['residual_emissions']:,.2f} tCO2e")
        st.json(offset_result)

    with tab_export:
        st.subheader("Export Center")
        run_payload = {
            "summary": {
                "total_emissions": baseline_total,
                "total_carbon_cost": selected_cost,
                "recommended_carbon_price": recommended_price,
                "selected_carbon_price": selected_carbon_price,
                "abatement_total_npv": abatement_result["total_npv"],
                "abatement_portfolio_irr": abatement_result.get("portfolio_irr"),
            },
            "settings": {
                "discount_rate_pct": discount_rate_pct,
                "analysis_years": analysis_years,
                "annual_savings_growth_pct": annual_savings_growth_pct,
            },
            "sections": {
                "Scope totals": emissions_result["scope_totals"],
                "Abatement": {
                    "total_reduction": abatement_result["total_reduction"],
                    "total_cost": abatement_result["total_cost"],
                    "total_net_value": abatement_result["total_net_value"],
                },
            },
            "data": {
                "activities": _to_json_records(activities_df),
                "pricing": _to_json_records(pricing_df),
                "department_emissions": _to_json_records(baseline_dept),
                "macc": _to_json_records(macc_df),
            },
        }

        pdf_bytes = build_pdf_report(run_payload)
        excel_bytes = build_excel_report(
            {
                "activities": activities_df,
                "pricing": pricing_df,
                "dept_emissions": baseline_dept,
                "macc": macc_df,
            }
        )

        st.download_button(
            "Download PDF report",
            data=pdf_bytes,
            file_name="carbonpricingx_report.pdf",
            mime="application/pdf",
        )
        st.download_button(
            "Download Excel report",
            data=excel_bytes,
            file_name="carbonpricingx_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
            "Download JSON simulation",
            data=json.dumps(run_payload, indent=2),
            file_name="carbonpricingx_run.json",
            mime="application/json",
        )

        if st.button("Save run to history"):
            run_path = save_run(run_payload, RUNS_DIR)
            st.session_state.last_saved_run = str(run_path)
            st.success(f"Saved: {run_path.name}")

        if st.session_state.last_saved_run:
            st.caption(f"Last saved run: {st.session_state.last_saved_run}")

    with tab_history:
        st.subheader("Historical Runs")
        runs = list_runs(RUNS_DIR)
        if not runs:
            st.info("No historical runs yet. Save one from Export Center.")
        else:
            run_map = {run.name: run for run in runs}
            selected = st.selectbox("Load run", list(run_map.keys()))
            loaded = load_run(run_map[selected])
            st.json(loaded.get("summary", {}))

            if len(runs) >= 2:
                names = list(run_map.keys())
                c_a, c_b = st.columns(2)
                run_a = c_a.selectbox("Run A", names, key="run_a")
                run_b = c_b.selectbox("Run B", names, index=1, key="run_b")
                if st.button("Compare selected runs"):
                    diff = compare_runs(run_map[run_a], run_map[run_b])
                    st.json(diff)
