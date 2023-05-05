import flask
import dash
import dash_bootstrap_components as dbc


server = flask.Flask(__name__)
app = dash.Dash(
    __name__,
    use_pages=True,
    server=server,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

if __name__ == "__main__":
    app.run(debug=True)