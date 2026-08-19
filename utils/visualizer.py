import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def auto_chart(df, chart_type, x_col=None, y_col=None, color_col=None):
    """Chart type ku ஏற்ப graph generate pannும்"""
    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, color=color_col)
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, color=color_col)
        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col, color=color_col)
        elif chart_type == "box":
            fig = px.box(df, x=x_col, y=y_col, color=color_col)
        else:
            return None
        fig.update_layout(template="plotly_white")
        return fig
    except Exception:
        return None


def correlation_heatmap(df):
    """Numeric columns correlation heatmap"""
    numeric_df = df.select_dtypes(include='number')
    if numeric_df.shape[1] < 2:
        return None
    corr = numeric_df.corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r")
    return fig


def forecast_chart(df, x_col, y_col, predictions, periods):
    """Actual data + Predicted future trend"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(len(df))),
        y=df[y_col],
        mode='lines+markers',
        name='Actual Data'
    ))

    future_x = list(range(len(df), len(df) + periods))
    fig.add_trace(go.Scatter(
        x=future_x,
        y=predictions,
        mode='lines+markers',
        name='Predicted (Forecast)',
        line=dict(dash='dash', color='red')
    ))

    fig.update_layout(title=f"Forecast: {y_col}", template="plotly_white")
    return fig


def dashboard_view(df, numeric_cols, categorical_cols):
    """PowerBI style - multiple mini charts oru grid la"""
    figs = []

    if len(numeric_cols) >= 1:
        fig1 = px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
        figs.append(fig1)

    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        grouped = df.groupby(categorical_cols[0])[numeric_cols[0]].sum().reset_index()
        fig2 = px.bar(grouped, x=categorical_cols[0], y=numeric_cols[0],
                       title=f"{numeric_cols[0]} by {categorical_cols[0]}")
        figs.append(fig2)

    if len(numeric_cols) >= 2:
        fig3 = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                           title=f"{numeric_cols[0]} vs {numeric_cols[1]}")
        figs.append(fig3)

    if len(categorical_cols) >= 1:
        count_data = df[categorical_cols[0]].value_counts().reset_index()
        count_data.columns = [categorical_cols[0], 'count']
        fig4 = px.pie(count_data, names=categorical_cols[0], values='count',
                       title=f"{categorical_cols[0]} Distribution")
        figs.append(fig4)

    return figs