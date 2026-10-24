"""Fonctions de graphiques : style cohérent, axes et unités toujours étiquetés."""
import plotly.express as px
import plotly.graph_objects as go

from .constants import REGIONS, SOURCE_COLORS, SOURCE_LABELS, SOURCES

FONT = dict(size=14)


def _style(fig, title=None, height=420):
    fig.update_layout(title=title, height=height, font=FONT, margin=dict(l=10, r=10, t=50, b=10),
                      legend_title_text="", plot_bgcolor="white", hovermode="x unified")
    fig.update_xaxes(showgrid=False, linecolor="#888")
    fig.update_yaxes(gridcolor="#e6e6e6", linecolor="#888")
    return fig


def line_chart(df, x, y, color=None, title=None, y_label="", x_label="Année", hline=None, hline_label=None,
               series_names=None):
    """y peut être une colonne ou une liste de colonnes (séries nommées via series_names)."""
    d = df
    if isinstance(y, list):
        d = df.melt(id_vars=[x], value_vars=y, var_name="Série", value_name="valeur")
        d["Série"] = d["Série"].map(series_names or {}).fillna(d["Série"])
        fig = px.line(d, x=x, y="valeur", color="Série", markers=True, labels={x: x_label, "valeur": y_label})
    else:
        labels = {x: x_label, y: y_label}
        if color:
            labels[color] = "Région"
        fig = px.line(d, x=x, y=y, color=color, markers=True, labels=labels)
    if hline is not None:
        fig.add_hline(y=hline, line_dash="dot", line_color="#b30000",
                      annotation_text=hline_label, annotation_position="top left")
    return _style(fig, title)


def stacked_mix(df, title=None):
    """Mix annuel empilé en TWh, une couleur fixe par source."""
    d = df.copy()
    long = d.melt(id_vars=["year"], value_vars=[f"{s}_mwh" for s in SOURCES],
                  var_name="source", value_name="mwh")
    long["source"] = long["source"].str.replace("_mwh", "", regex=False)
    long["twh"] = long["mwh"] / 1e6
    long["Source"] = long["source"].map(SOURCE_LABELS)
    fig = px.area(long, x="year", y="twh", color="Source",
                  color_discrete_map={SOURCE_LABELS[s]: SOURCE_COLORS[s] for s in SOURCES},
                  category_orders={"Source": [SOURCE_LABELS[s] for s in SOURCES]},
                  labels={"year": "Année", "twh": "Production (TWh)"})
    return _style(fig, title)


def bar_chart(df, x, y, title=None, x_label="", y_label="", color=None, horizontal=True, text_fmt=".0f"):
    d = df.sort_values(x if horizontal else y, ascending=True)
    fig = px.bar(d, x=x, y=y, orientation="h" if horizontal else "v", color=color,
                 labels={x: x_label, y: y_label}, text=x if horizontal else y)
    fig.update_traces(texttemplate="%{text:" + text_fmt + "}", textposition="outside", cliponaxis=False)
    fig.update_layout(coloraxis_showscale=False)
    return _style(fig, title, height=max(380, 34 * len(d) + 120))


def small_multiples(df, x, y, facet, title=None, y_label="", x_label="Année", cols=4):
    fig = px.line(df, x=x, y=y, facet_col=facet, facet_col_wrap=cols,
                  labels={x: x_label, y: y_label})
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_yaxes(matches="y")
    return _style(fig, title, height=620)


def map_chart(df, value, geojson, label, title=None):
    """Carte choroplèthe si le GeoJSON est disponible, sinon bulles sur les centroïdes."""
    d = df.copy()
    if geojson is not None:
        fig = px.choropleth_map(d, geojson=geojson, locations="region_code", featureidkey="properties.code",
                                color=value, hover_name="region", color_continuous_scale="Viridis",
                                labels={value: label}, map_style="carto-positron",
                                center={"lat": 46.6, "lon": 2.4}, zoom=4.3, opacity=0.8)
    else:
        d["lat"] = d["region"].map(lambda r: REGIONS[r][1])
        d["lon"] = d["region"].map(lambda r: REGIONS[r][2])
        d["size"] = d[value].clip(lower=1)
        fig = px.scatter_map(d, lat="lat", lon="lon", size="size", color=value, hover_name="region",
                             color_continuous_scale="Viridis", labels={value: label}, size_max=40,
                             map_style="carto-positron", center={"lat": 46.6, "lon": 2.4}, zoom=4.3)
    fig.update_layout(height=560, margin=dict(l=0, r=0, t=40, b=0), title=title, font=FONT)
    return fig
