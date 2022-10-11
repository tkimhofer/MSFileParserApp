from dash import Dash, html, dcc, callback, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import dash_mantine_components as dmc
from scr import conv
import logging as l
from flask import Flask
import datetime as dt

logger = l.getLogger('ct')
logger.setLevel(l.DEBUG)
ch = l.StreamHandler()
ch.setLevel(l.DEBUG)
formatter = l.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


server = Flask(__name__) # define flask app.server
# app = Dash(__name__, server=server)

external_stylesheets = [
    # "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap",
    # 'https://fonts.googleapis.com/css2?family=Freehand&display=swap',
'https://fonts.googleapis.com/css2?family=Play&display=swap'
]
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, server=server, suppress_callback_exceptions=True)
app.title='MS-FP'

app.layout = dmc.MantineProvider(
    children = [
        html.Div(children=[
        html.H1(children='MS file parser', style={"font-family": "'Play'"}),
        html.Div(#dmc.Container([
        dmc.Group(children=[
            dmc.Chips(
                id="vartype",
                data=[
                    {"value": "Conc.", "label": "Concentration"},
                    {"value": "Response", "label": "Response",},
                    {"value": "Area", "label": "Area",}
                ],
                value="Conc.",
            ),
            dmc.Space(h=10),
            dmc.Checkbox(
                id="includeIS",
                label="include internal Stds",
            )
        ], position='left')
),
            dmc.Space(h=10),
        dmc.Space(h=10),
        dcc.Upload(id='upload-data', children=['Drag and Drop or ', html.A('Select a File')], style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center'
        }, multiple=True),
        # html.Button("Download CSV", id="btn_csv"),
        dcc.Download(id="download-dataframe-csv"),
        dcc.Loading(id='loadingTbl', children=[html.Div(id='output_downloadBtn'), dmc.Space(h=30), html.Div(id='output-summary'), html.Div(id='output-data-upload')], type="cube", fullscreen=True, color='#8151FD')
        # html.Div(id='output-data-upload'),
            ])
])

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State('vartype', 'value'),
    State("includeIS", "checked"),
    prevent_initial_call=True
)
def func(n_clicks, vtype, intStd):
    if n_clicks is not None:
        now = dt.datetime.now().strftime("%d-%m %H:%M:%S")
        sil = 'noSIL'if not bool(intStd) else 'withSil'
        return dcc.send_data_frame(df.to_csv, f"df_{vtype.replace('.', '').lower()}_{sil}_{now}_.csv")

@app.callback(Output('output-data-upload', 'children'),
              Output('output_downloadBtn', 'children'),
              Output('output-summary', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              Input('vartype', 'value'),
              Input("includeIS", "checked"),
              prevent_initial_call=True
              )
def update_output(list_of_contents, list_of_names, vtype, inIS):
    if list_of_contents is not None:
        global df
        df = conv.readbin(list_of_contents, list_of_names, varType=vtype, sil=bool(inIS))
        children = [
            html.Div([
                html.Hr(),
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'name': i, 'id': i, 'type': ('text' if i in['path', 'Name', 'Sample Text'] else 'numeric')} for i in df.columns],
                    # columns=[{'name': i, 'id': i, } for i in df.columns],
                    page_size=30,  # we have less data in this example, so setting to 20
                    style_table={'overflowY': 'auto'},
                    sort_action='native',
                    filter_action='native',
                    style_header={
                        'whiteSpace': 'normal',
                        'minHeight': '100px', 'height': '110px', 'maxHeight': '150px',
                        'minWidth': '100px', 'width': '110px', 'maxWidth': '150px',
                        # 'lineHeight': '15px'
                    },
                    style_data={
                        # 'whiteSpace': 'normal',
                        'minWidth': '100px', 'width': '110px', 'maxWidth': '150px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        # 'maxWidth': 0,
                    },
                    tooltip_data=[
                        {column: {'value': '\n'.join(value.split('_')) , 'type': 'markdown'} for column, value in row.items() if column in  ['Name', 'Sample Text'] } for row in df.to_dict('records')
                    ],
                    tooltip_duration=None,
                    style_cell={
                        'fontFamily': 'Open Sans',
                        'textAlign': 'center',}
                )])]
        c1 = [html.Hr(), dmc.Button("Download CSV", id="btn_csv", variant="gradient",
                   gradient={"from": "teal", "to": "lime", "deg": 105})]

        dims = dmc.Text(f'{df.shape[0]} samples x {df.shape[1]} analytes')
        return children, c1, dims


if __name__ == '__main__':
    app.run_server(debug=True)