from random import randint
from pprint import pp


def rand_bool():
    return randint(0, 1)


def gen_tree():
    # probability question: What is the Expected number of nodes in this tree?
    child_counter = 0
    node_process_queue = ['0']
    nodes = []
    edges = []
    while node_process_queue:
        if rand_bool():
            parent = node_process_queue[0]
            child = parent + '.' + str(child_counter)
            node_process_queue.append(child)
            edges.append((parent, child))
            child_counter += 1
        else:
            child_counter = 0
            nodes.append(node_process_queue.pop(0))
    return {'nodes': nodes, 'edges': edges}


def gen_tree_history():
    final_tree = gen_tree()
    final_nodes = final_tree['nodes']
    final_edges = final_tree['edges']
    assert len(final_nodes) == len(final_edges) + 1

    n = len(final_nodes)
    history_nodes = [final_nodes[:i+1] for i in range(n)]
    history_edges = [final_edges[:i] for i in range(n)]  # There are no edges at first.
    history_trees = [{'nodes': history_nodes[i], 'edges': history_edges[i]}
                     for i in range(len(final_nodes))]
    return history_trees


def get_static_tree(verbose=False):
    # edges are a list of tuples/sets
    edges = [
        ('node1', 'node1.1'),
        ('node1', 'node1.2'),
        ('node1', 'node1.3'),
        ('node1.1', 'node1.1.1'),
        ('node1.1', 'node1.1.2'),
        ('node1.2', 'node1.2.1'),
        ('node1.2', 'node1.2.2'),
        ('node1.2', 'node1.2.3'),
        ('node1.3', 'node1.3.1'),
        ('node1.3', 'node1.3.2'),
        ('node1.1.1', 'node1.1.1.1'),
        ('node1.1.1', 'node1.1.1.2'),
        ('node1.3.1', 'node1.3.1.1'),
        ('node1.3.1', 'node1.3.1.2'),
        ('node1.3.1', 'node1.3.1.3'),
    ]

    # nodes should be a dictionary (key=ID, value=properties dict)
    node_set = set()
    for edge in edges:
        node_set = node_set.union(edge)

    nodes = {}
    color_bool = True
    for node in sorted(node_set):
        nodes[node] = {
            'color': 'red' if color_bool else 'blue',
            'json': 'specific info to node can go here, like a json of information',
        }
        color_bool = not color_bool  # We alternate colors

    # Here is our data:
    if verbose:
        print('The nodes are: {}'.format(nodes.keys()))
        print('The edges are: ')
        pp(edges)

    # df = pd.DataFrame.from_dict(nodes, orient='index')

    return {'edges': edges, 'nodes': nodes}
