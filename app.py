from dash import Dash, html, dcc, callback, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from scr import conv
import logging as l

logger = l.getLogger('ct')
logger.setLevel(l.DEBUG)

# create console handler and set level to debug
ch = l.StreamHandler()
ch.setLevel(l.DEBUG)

# create formatter
formatter = l.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# # 'application' code
# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('kiss kiss')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(children=[
    html.H1(children='MS file parser'),
    dcc.Upload(id='upload-data', children=['Drag and Drop or ', html.A('Select a File')], style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center'
    }, multiple=True),
    html.Hr(),
    html.Button("Download CSV", id="btn_csv"),
    dcc.Download(id="download-dataframe-csv"),
    html.Div(id='output-data-upload'),
])

# def fileparser(contentlist, filelist):
#     # import datetime
#     ds = conv.readbin(contentlist, filelist)
#     # try:
#     #     ds = conv.readbin(contentlist, filelist)
#     #     if ds is None:
#     #         return html.Div([
#     #             'There was an error processing this file.'
#     #         ])
#     #
#     # except:
#     #     return html.Div([
#     #         'There was an error processing this file.'
#     #     ])
#
#     # html.H5(filename),
#     # html.H6(datetime.datetime.fromtimestamp(date)),
#     return ds
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True)
def func(n_clicks):
    return dcc.send_data_frame(df.to_csv, "mydf.csv")



@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        global df
        df = conv.readbin(list_of_contents, list_of_names)
        children = [
            html.Div([
                html.Hr(),
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'name': i, 'id': i, 'type': ('numeric' if i != 'id' else 'text')} for i in df.columns],
                    sort_action='native',
                    filter_action='native',
                    sort_mode = 'multi',
                    #row_selectable="multi",
                    page_size=50,
                    # row_deletable=True,
                    # table style (ordered by increased precedence: see
                    # https://dash.plot.ly/datatable/style in § "Styles Priority"
                    # style table
                    style_data = {
                        'whiteSpace': 'normal',
                        'height': 'auto',
                    },
                    style_table={
                        #'maxHeight': '50ex',
                        'overflowX': 'auto',
                        'overflowY': 'auto',
                        'width': '100%',
                        'minWidth': '100%',
                    },
                    # style cell
                    style_cell={
                        'fontFamily': 'Open Sans',
                        'textAlign': 'center',
                        # 'height': 'auto',
                        # 'widtj': 'auto',
                        # 'padding': '2px 22px',
                        # 'whiteSpace': 'inherit',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                    },
                    # style header
                    style_header={
                        'fontWeight': 'bold',
                        'backgroundColor': 'white',
                    },

                    style_cell_conditional=[
                        {
                            'if': {'column_id': 'id'},
                            'textAlign': 'left'
                        }
                    ]


                )])
        ]
        return children


if __name__ == '__main__':
    app.run_server(debug=True)