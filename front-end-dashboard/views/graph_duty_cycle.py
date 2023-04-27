import plotly.graph_objects as go
from dash import dcc, html


#global df_energy
df_energy = None

graph_duty_cycle = html.Div(
    children=[
        html.Div("Duty Cycle Levels", className='graph-title'),
        dcc.Graph(id="graph_duty_cycle",
            figure=go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=0,
                    domain={"x": [0, 1], "y": [0, 1]},
                    delta={"reference": 1200},
                    title={"text": "Energy Consumption"},
                    gauge={
                        "axis": {"range": [None, 1200]},
                        "steps": [
                            {"range": [0, 400], "color": "gray"},
                        ],
                    },
                ),
                layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
            ),
        ),
    ]
)

