from __future__ import annotations

import unicodedata
from typing import Any

try:
    import plotly.graph_objects as go
except ImportError:  # pragma: no cover - exercised when plotly.py is installed.
    go = None


def build_visualization(question: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return _disabled("No data available for visualization.")

    shape = _detect_shape(rows)
    if not shape:
        return _disabled("Result shape is not suitable for a chart.")

    label_column, metric_column = shape
    kind = _chart_kind(question, label_column)
    title = _chart_title(question, label_column, metric_column)
    sorted_rows = _sort_rows(rows, metric_column, kind)
    labels = [row.get(label_column) for row in sorted_rows]
    values = [row.get(metric_column) for row in sorted_rows]

    return {
        "enabled": True,
        "kind": kind,
        "title": title,
        "figure": _build_figure(kind, title, label_column, metric_column, labels, values),
        "reason": None,
    }


def _build_figure(
    kind: str,
    title: str,
    label_column: str,
    metric_column: str,
    labels: list[Any],
    values: list[Any],
) -> dict[str, Any]:
    if go is not None:
        if kind == "line":
            figure = go.Figure(
                data=[
                    go.Scatter(
                        x=labels,
                        y=values,
                        mode="lines+markers",
                        line={"color": "#44d5b2", "width": 3},
                        marker={"color": "#f1aa6b", "size": 7},
                        hovertemplate="%{x}<br>%{y:,.2f}<extra></extra>",
                    )
                ]
            )
        elif kind == "horizontal_bar":
            figure = go.Figure(
                data=[
                    go.Bar(
                        x=values,
                        y=labels,
                        orientation="h",
                        marker={"color": "#44d5b2"},
                        hovertemplate="%{y}<br>%{x:,.2f}<extra></extra>",
                    )
                ]
            )
        else:
            figure = go.Figure(
                data=[
                    go.Bar(
                        x=labels,
                        y=values,
                        marker={"color": "#44d5b2"},
                        hovertemplate="%{x}<br>%{y:,.2f}<extra></extra>",
                    )
                ]
            )
        figure.update_layout(**_layout(title, label_column, metric_column, kind, labels))
        figure_dict = figure.to_dict()
        figure_dict["config"] = _config()
        return figure_dict

    trace = _manual_trace(kind, labels, values)
    return {
        "data": [trace],
        "layout": _layout(title, label_column, metric_column, kind, labels),
        "config": _config(),
    }


def _manual_trace(kind: str, labels: list[Any], values: list[Any]) -> dict[str, Any]:
    if kind == "line":
        return {
            "type": "scatter",
            "mode": "lines+markers",
            "x": labels,
            "y": values,
            "line": {"color": "#44d5b2", "width": 3},
            "marker": {"color": "#f1aa6b", "size": 7},
            "hovertemplate": "%{x}<br>%{y:,.2f}<extra></extra>",
        }
    if kind == "horizontal_bar":
        return {
            "type": "bar",
            "orientation": "h",
            "x": values,
            "y": labels,
            "marker": {"color": "#44d5b2"},
            "hovertemplate": "%{y}<br>%{x:,.2f}<extra></extra>",
        }
    return {
        "type": "bar",
        "x": labels,
        "y": values,
        "marker": {"color": "#44d5b2"},
        "hovertemplate": "%{x}<br>%{y:,.2f}<extra></extra>",
    }


def _layout(
    title: str,
    label_column: str,
    metric_column: str,
    kind: str,
    labels: list[Any],
) -> dict[str, Any]:
    layout = {
        "title": {"text": title},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#edf5fb"},
        "margin": {"l": 48, "r": 18, "t": 52, "b": 56},
        "xaxis": {
            "title": {"text": _humanize(label_column)},
            "gridcolor": "rgba(255,255,255,0.08)",
            "tickangle": -20 if kind == "bar" and len(labels) > 4 else 0,
        },
        "yaxis": {
            "title": {"text": _humanize(metric_column)},
            "gridcolor": "rgba(255,255,255,0.08)",
        },
    }
    if kind == "horizontal_bar":
        layout["xaxis"]["title"]["text"] = _humanize(metric_column)
        layout["yaxis"]["title"]["text"] = _humanize(label_column)
        layout["yaxis"]["autorange"] = "reversed"
        layout["margin"] = {"l": 120, "r": 18, "t": 52, "b": 42}
    return layout


def _config() -> dict[str, Any]:
    return {
        "displaylogo": False,
        "responsive": True,
    }


def _detect_shape(rows: list[dict[str, Any]]) -> tuple[str, str] | None:
    columns = list(rows[0].keys())
    numeric_columns = [
        column
        for column in columns
        if all(_is_number(row.get(column)) for row in rows)
    ]
    label_columns = [
        column
        for column in columns
        if all(not _is_number(row.get(column)) for row in rows)
    ]
    for semantic_label in ["month_name", "full_date", "year", "month"]:
        if semantic_label in columns and semantic_label not in label_columns:
            label_columns.append(semantic_label)

    if not numeric_columns or not label_columns:
        return None

    return label_columns[0], _preferred_metric(numeric_columns)


def _preferred_metric(columns: list[str]) -> str:
    for candidate in ["revenue", "margin", "quantity", "cost"]:
        if candidate in columns:
            return candidate
    return columns[0]


def _chart_kind(question: str, label_column: str) -> str:
    normalized = _normalize(question)
    if label_column in {"month_name", "month", "full_date", "year"}:
        return "line"
    if any(word in normalized for word in ["mois", "mensuel", "monthly", "month"]):
        return "line"
    if any(word in normalized for word in ["top", "meilleur", "meilleurs", "classement"]):
        return "horizontal_bar"
    return "bar"


def _chart_title(question: str, label_column: str, metric_column: str) -> str:
    normalized = _normalize(question)
    metric = _humanize(metric_column)
    label = _humanize(label_column)
    if "top" in normalized:
        return f"Top {label} par {metric}"
    if any(word in normalized for word in ["mois", "mensuel", "monthly", "month"]):
        return f"{metric} par mois"
    if any(word in normalized for word in ["evolution", "variation", "croissance"]):
        return f"Evolution de {metric}"
    return f"{metric} par {label}"


def _sort_rows(rows: list[dict[str, Any]], metric_column: str, kind: str) -> list[dict[str, Any]]:
    if kind == "line":
        return rows
    sorted_rows = sorted(rows, key=lambda row: row.get(metric_column) or 0, reverse=True)
    if kind == "horizontal_bar":
        return sorted_rows[:10]
    return sorted_rows


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _humanize(value: str) -> str:
    return value.replace("_", " ").title()


def _normalize(text: str) -> str:
    without_accents = unicodedata.normalize("NFKD", text)
    return "".join(char for char in without_accents if not unicodedata.combining(char)).lower()


def _disabled(reason: str) -> dict[str, Any]:
    return {
        "enabled": False,
        "kind": None,
        "title": None,
        "figure": None,
        "reason": reason,
    }
