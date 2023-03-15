"""
Front-End

Renders UI dashboard and updates figures intermittently using callbacks

TODO:

1. Figure out how to visualise and create required metrics in Dash
2. Figure out format of updates and frequency
3. Design and implement based on 1 + 2
"""

import json
from datetime import datetime

import dash
import flask
import plotly.graph_objs as go
from dash import Input, Output, dcc, html
from flask import request

# declare global variables that will be updated by AAS
global bar_graph_yaxis
bar_graph_yaxis = [0]

global time
time_graph_xaxis = ["None"]

text_style = {
    "color": "blue",
}

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

app.layout = html.Div(
    [
        dcc.Interval(
            id="interval-component",
            interval=3 * 1000,  # in milliseconds check for updates
        ),
        html.Div(
            id="dummy",
            children=f"Number of documents sent: {bar_graph_yaxis}",
            style=text_style,
        ),
        dcc.Graph(
            id="graph-updates",
            figure=go.Figure(data=[go.Bar(x=[1, 2, 3], y=[4, 1, 2])]),
        ),
    ]
)


@app.callback(
    Output("dummy", "style"),
    Output("dummy", "children"),
    Output("graph-updates", "figure"),
    [Input("interval-component", "n_intervals")],
)
def timer(n_intervals):
    fig = go.Figure(data=[go.Bar(x=time_graph_xaxis, y=bar_graph_yaxis)])

    return (
        text_style,
        f"Number of documents sent: {bar_graph_yaxis[-1]} at {time_graph_xaxis[-1]}",
        fig,
    )


@server.route("/data-update", methods=["POST"])
def req():
    if (
        text_style["color"] == "blue"
    ):  # Toggle textcolor between red and blue as an example of how we can change styles
        text_style["color"] = "red"
    else:
        text_style["color"] = "blue"

    print(f"data received = {request.json}")

    # Update the graph with data from AAS
    global bar_graph_yaxis, time_graph_xaxis
    bar_graph_yaxis.append(
        request.json["UPDATE_COUNT"]
    )  # use data from post request (AAS)
    time_graph_xaxis.append(
        datetime.now().strftime("%H:%M:%S")
    )  # update when we received AAS post data

    # return OK/sucess reponse to AAS
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


if __name__ == "__main__":
    app.run_server(debug=True)
