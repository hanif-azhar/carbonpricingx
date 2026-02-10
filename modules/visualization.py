from __future__ import annotations

import pandas as pd
import plotly.express as px

PALETTE = ["#0f766e", "#14b8a6", "#0284c7", "#22c55e", "#f59e0b", "#ef4444"]


def style_figure(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0.72)",
        plot_bgcolor="rgba(248,250,252,0.94)",
        font={"family": "Space Grotesk, Avenir Next, Segoe UI, sans-serif", "color": "#10231d", "size": 14},
        title={"font": {"size": 22, "color": "#10231d"}, "x": 0.01},
        colorway=PALETTE,
        margin={"l": 40, "r": 24, "t": 64, "b": 40},
        legend={
            "bgcolor": "rgba(255,255,255,0.85)",
            "bordercolor": "rgba(16,35,29,0.18)",
            "borderwidth": 1,
            "font": {"color": "#10231d"},
        },
        xaxis={
            "gridcolor": "rgba(16,35,29,0.08)",
            "zerolinecolor": "rgba(16,35,29,0.15)",
            "linecolor": "rgba(16,35,29,0.15)",
            "tickfont": {"color": "#10231d"},
            "title_font": {"color": "#10231d"},
        },
        yaxis={
            "gridcolor": "rgba(16,35,29,0.08)",
            "zerolinecolor": "rgba(16,35,29,0.15)",
            "linecolor": "rgba(16,35,29,0.15)",
            "tickfont": {"color": "#10231d"},
            "title_font": {"color": "#10231d"},
        },
        coloraxis_colorbar={"tickfont": {"color": "#10231d"}, "title": {"font": {"color": "#10231d"}}},
    )
    fig.update_traces(marker_line_width=1, marker_line_color="rgba(16,35,29,0.18)")
    return fig


def pricing_cost_curve(df: pd.DataFrame):
    fig = px.line(df, x="carbon_price", y="carbon_cost", markers=True, title="Carbon Cost Curve")
    return style_figure(fig)


def emissions_vs_price(df: pd.DataFrame):
    fig = px.line(df, x="carbon_price", y="adjusted_emissions", markers=True, title="Emissions vs Carbon Price")
    return style_figure(fig)


def fee_distribution(df: pd.DataFrame):
    fig = px.bar(df, x="department", y="fee_cost", title="Department Fee Distribution")
    return style_figure(fig)


def behavior_response(df: pd.DataFrame):
    view = df[["department", "emissions_tonnes", "adjusted_emissions"]].melt(
        id_vars="department",
        var_name="series",
        value_name="value",
    )
    fig = px.bar(view, x="department", y="value", color="series", barmode="group", title="Behavior Response")
    return style_figure(fig)


def macc_curve(df: pd.DataFrame):
    fig = px.bar(
        df,
        x="initiative_name",
        y="reduction_tonnes",
        color="cost_per_tonne",
        title="MAC Curve",
        color_continuous_scale="Teal",
    )
    return style_figure(fig)


def cumulative_reduction(df: pd.DataFrame):
    fig = px.line(df, x="initiative_name", y="cumulative_reduction", markers=True, title="Cumulative Reduction")
    return style_figure(fig)


def roi_timeline(df: pd.DataFrame):
    roi_df = df.copy()
    roi_df["roi_years"] = pd.to_numeric(roi_df["roi_years"], errors="coerce")
    roi_df = roi_df.dropna(subset=["roi_years"])
    if roi_df.empty:
        roi_df = pd.DataFrame({"initiative_name": [], "roi_years": []})
    fig = px.bar(roi_df, x="initiative_name", y="roi_years", title="ROI Timeline (Years)")
    return style_figure(fig)


def npv_by_initiative(df: pd.DataFrame):
    npv_df = df.copy()
    npv_df["npv"] = pd.to_numeric(npv_df["npv"], errors="coerce")
    npv_df = npv_df.dropna(subset=["npv"])
    if npv_df.empty:
        npv_df = pd.DataFrame({"initiative_name": [], "npv": []})
    fig = px.bar(npv_df, x="initiative_name", y="npv", title="NPV by Initiative")
    return style_figure(fig)
