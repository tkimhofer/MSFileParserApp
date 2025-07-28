from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_mantine_components as dmc
import pandas as pd
from scr import conv
from flask import Flask
import datetime as dt
import logging


logger = logging.getLogger('ct')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


server = Flask(__name__)
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Play&display=swap']

app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    server=server,
    suppress_callback_exceptions=True
)
app.title = 'MS-FP'


app.layout = dmc.MantineProvider([
    html.Div([
        html.H1('MS file parser', style={"font-family": "'Play'"}),
        dmc.Group([
            dmc.ChipGroup(
                id="vartype",
                value="Conc.",
                multiple=False,
                children=[
                    dmc.Chip(value="Conc.", label="Concentration"),
                    dmc.Chip(value="Response", label="Response"),
                    dmc.Chip(value="Area", label="Area"),
                ],
            ),
            dmc.Checkbox(id="includeIS", label="Include internal Stds")
        ], justify='flex-start'),

        dmc.Space(h=10),

        dcc.Upload(
            id='upload-data',
            children=['Drag and Drop or ', html.A('Select a File')],
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed',
                'borderRadius': '5px', 'textAlign': 'center'
            },
            multiple=True
        ),

        dcc.Download(id="download-dataframe-csv"),

        dcc.Loading(
            id='loadingTbl',
            children=[
                html.Div(id='output_downloadBtn'),
                dmc.Space(h=30),
                html.Div(id='output-summary'),
                html.Div(id='output-data-upload')
            ],
            type="cube",
            fullscreen=True,
            color='#8151FD'
        )
    ])
])


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State("vartype", "value"),
    State("includeIS", "checked"),
    prevent_initial_call=True
)
def download_csv(n_clicks, vtype, int_std):
    if n_clicks:
        now = dt.datetime.now().strftime("%d-%m_%H-%M-%S")
        sil = 'noSIL' if not int_std else 'withSIL'
        return dcc.send_data_frame(df.to_csv, f"df_{vtype.replace('.', '').lower()}_{sil}_{now}.csv")

@app.callback(
    Output('output-data-upload', 'children'),
    Output('output_downloadBtn', 'children'),
    Output('output-summary', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    Input('vartype', 'value'),
    Input('includeIS', 'checked'),
    prevent_initial_call=True
)
def update_output(list_of_contents, list_of_names, vtype, include_is):
    if list_of_contents:
        global df
        df = conv.readbin(list_of_contents, list_of_names, varType=vtype, sil=bool(include_is))

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                {'name': i, 'id': i, 'type': 'text' if i in ['path', 'Name', 'Sample Text'] else 'numeric'}
                for i in df.columns
            ],
            page_size=30,
            style_table={'overflowY': 'auto'},
            sort_action='native',
            filter_action='native',
            tooltip_data=[
                {
                    column: {'value': '\n'.join(value.split('_')), 'type': 'markdown'}
                    for column, value in row.items() if column in ['Name', 'Sample Text']
                }
                for row in df.to_dict('records')
            ],
            tooltip_duration=None,
            style_cell={'fontFamily': 'Open Sans', 'textAlign': 'center'},
            style_header={
                'whiteSpace': 'normal', 'minHeight': '100px', 'height': '110px',
                'minWidth': '100px', 'width': '110px', 'maxWidth': '150px'
            },
            style_data={
                'minWidth': '100px', 'width': '110px', 'maxWidth': '150px',
                'overflow': 'hidden', 'textOverflow': 'ellipsis'
            }
        )

        download_btn = dmc.Button("Download CSV", id="btn_csv", variant="gradient",
                                  gradient={"from": "teal", "to": "lime", "deg": 105})

        summary = dmc.Text(f'{df.shape[0]} samples x {df.shape[1]} analytes')

        return [html.Div([html.Hr(), table])], [html.Hr(), download_btn], summary

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
