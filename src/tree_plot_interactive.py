
# EXTERNAL PACKAGE IMPORTS
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from pprint import pp

from dash.dependencies import Input, Output, State

# MY PACKAGES
import random_tree_gen


# START WEB APP
cyto.load_extra_layouts()
app = dash.Dash(__name__)


# GET DATA
def get_elements_from_tree(tree):
    nodes = tree['nodes']
    edges = tree['edges']
    elements_nodes = [{'data': {'id': node, 'label': node}} for node in nodes]
    elements_edges = [{'data':
                           {'source': nodes[0], 'target': nodes[1], 'id': nodes[0] + '-->' + nodes[1]}
                       } for nodes in edges]
    return elements_nodes + elements_edges


def generate_tree():
    res = random_tree_gen.gen_tree_history()
    while not 5 < len(res) < 20:
        res = random_tree_gen.gen_tree_history()
    return res


trees = generate_tree()
elements = get_elements_from_tree(trees[-1])
times = list(range(len(trees)))


# PLOT DATA
# https://dash.plotly.com/cytoscape

app.layout = html.Div([

    html.H1(
        children='Tree plot',
        style={
            'text-align': 'center',
            'font-size': '4vh',
            'margin-top': '0',
            'margin-bottom': '0',
        },
    ),

    html.Div(
        style={
            'margin-top': '0',
            'margin-bottom': '0',
        },
        children=[
            html.Button(
                children="Toggle Graph Layout",
                id='toggle-button',
                n_clicks=0,
                style={
                    'display': 'inline-block',
                }
            ),
            html.Button(
                children="Regenerate Tree",
                id='regenerate-button',
                n_clicks=0,
                style={
                    'display': 'inline-block',
                }
            ),
        ]
    ),

    html.Br(),

    html.Br(),

    html.Div(
        id='slider-div',
        style={'width': '85%', 'margin': 'auto'},  # margin=auto means center the div
        children=
        dcc.Slider(
            id='slider',
            step=None,
            marks={
                time: {
                    'label': str(time),
                    'style': {'font-size': '3vh', 'font-weight': 'bold', 'color': 'black'},
                }
                for time in times
            },
            min=min(times),
            max=max(times),
            value=max(times),
        ),
    ),

    html.Div(
        children=[
        cyto.Cytoscape(
            # The layout property is set by the "toggle_layout" callback below
            id='tree',
            elements=[],  # The element property is updated by the callback below
            style={
                'width': '50%',
                'height': '85vh',
                'border': 'dashed thin',
                'display': 'inline-block',
            },
            minZoom=0.25,
            maxZoom=10,
            responsive=True,
            stylesheet=[
                {
                    'selector': 'node',
                    'style': {'content': 'data(label)'}
                },
                {
                    'selector': 'edge',
                    'style': {
                        'target-arrow-shape': 'triangle',
                        'target-arrow-fill': 'filled',
                        'curve-style': 'bezier',
                    }
                },
                {
                    'selector': 'edge.bold',
                    'style': {
                        'line-color': 'black',  # controls edge color
                        'target-arrow-color': 'black',  # controls arrow color (part of edge)
                        'font-weight': 'bold',
                        'width': 10,
                    }
                },
                {
                    'selector': 'node.bold',
                    'style': {
                        'background-color': 'black',  # Controls node color
                        'color': 'black',  # Controls label color
                        'font-weight': 'bold',
                        'width': 40,
                        'height': 40,
                    }
                },
            ],
        ),

        html.Pre(id='node-info')  # style set in callback below
    ])
])


@app.callback(
    [Output('node-info', 'children'), Output('node-info', 'style')],
    Input('tree', 'tapNodeData')
)
def display_node_data(data):
    if data is None:
        return None, {}
    style = {
        'border': 'solid thin',
        'font-weight': 'bold',
        'width': '45%',
        'display': 'inline-block',
        'vertical-align': 'top',
        'margin-top': '0',
    }
    return "Here we can display data about node: " + data['id'], style


@app.callback(
    [
        Output('tree', 'elements'),
        Output('slider-div', 'children'),
    ],
    [
        Input('slider', 'value'),
        Input('regenerate-button', 'n_clicks'),
    ],
    [
        State('tree', 'elements'),  # This is the "old tree"
        State('slider-div', 'children'),  # This is the old dcc slider object
    ]
)
def update_tree(slider_value, n_clicks, old_tree, old_slider):
    # Dash forces us to combine 2 callbacks into 1 because we can't have the same Output from >1 callback.
    def update_from_slider(slider_value, old_tree):
        """
        Updates the tree based on the slider. Makes any added nodes/edges bold.
        Will need to edit this function if there are changed (but now added) nodes/edges.
        """
        def reset_classes(tree):
            for i in range(len(tree)):
                tree[i]['classes'] = []
            return tree

        global trees
        new_tree = get_elements_from_tree(trees[slider_value])
        new_tree = reset_classes(new_tree)
        old_tree = reset_classes(old_tree)
        diffs = [elt for elt in new_tree if elt not in old_tree]
        if not diffs:
            return new_tree

        for element in diffs:
            element['classes'] = ['bold']
        return old_tree + diffs

    def update_from_button():
        global trees, elements, times
        trees = generate_tree()
        elements = get_elements_from_tree(trees[-1])
        times = list(range(len(trees)))

        child = dcc.Slider(
            id='slider',
            step=None,
            marks={
                time: {
                    'label': str(time),
                    'style': {'font-size': '3vh', 'font-weight': 'bold', 'color': 'black'},
                }
                for time in times
            },
            min=min(times),
            max=max(times),
            value=max(times),
        ),
        return elements, child

    # Use the functions above depending on context (ie what triggered the callback)
    context = dash.callback_context
    if not context.triggered:
        prop = None
    else:
        _, prop = context.triggered[0]['prop_id'].split('.')

    if prop != 'n_clicks':
        return update_from_slider(slider_value, old_tree), old_slider

    return update_from_button()


@app.callback(
    Output('tree', 'layout'),
    Input('toggle-button', 'n_clicks')
)
def toggle_layout(n_clicks):
    layout = {
        'name': 'breadthfirst',
        'roots': '[id = "0"]',
        'directed': True,
        'animate': True,
        'animationEasing': 'ease-out',
    }
    if n_clicks % 2 == 0:
        return layout
    layout['name'] = 'dagre'
    return layout


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)  # debug=True)
