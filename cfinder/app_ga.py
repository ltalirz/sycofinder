# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from cfinder import app

import pandas as pd

from . import ga
from .common import HIDE, SHOW, generate_table

layout = html.Div([
    dcc.Upload(
        id='upload_data',
        children=html.Div(['Drag and Drop or ',
                           html.A('Select Files')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False),
    html.Div(id='parsed_data', style=HIDE),
    html.Div(id='parsed_data_table'),
    html.Div(
        [
            html.Button('compute', id='btn_compute'),
            html.Div('', id='ga_compute_info')
        ],
        id='div_compute')
])


@app.callback(
    Output('parsed_data', 'children'), [
        Input('upload_data', 'contents'),
        Input('upload_data', 'filename'),
        Input('upload_data', 'last_modified')
    ])
def parse_data(content, name, date):
    if content is None:
        return ''

    from .common import validate_df, parse_contents

    df = parse_contents(content, name, date)
    validate_df(df)
    return df.to_json(date_format='iso', orient='split')


@app.callback(
    Output('div_compute', 'style'), [Input('parsed_data', 'children')])
def show_button(json):
    if json is None:
        return HIDE
    return SHOW


#@app.callback(Output('parsed_data_table', 'children'), [Input('parsed_data', 'children')])
#def show_data(json):
#    if json is None:
#        return ''
#    df = pd.read_json(json, orient='split')
#    return generate_table(df, download_link=False)
#
@app.callback(
    Output('ga_compute_info', 'children'), [Input('btn_compute', 'n_clicks')],
    [State('parsed_data', 'children')])
# pylint: disable=unused-argument, unused-variable
def on_compute(n_clicks, json):
    if json is None:
        return
    df = pd.read_json(json, orient='split')

    new_pop, variables = ga.main(input_data=df.values, var_names=list(df))
    df_new = pd.DataFrame(new_pop, columns=variables)
    df_new['Fitness'] = ""

    return generate_table(df_new, download_link=True)
