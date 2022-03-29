import networkx as nx
import re
import copy
from typing import Tuple
from bit_stream_funcs import Clb
import config as cfg


def reverse_link(link: tuple) -> tuple:
    """
    Reverses the first and second element of the tuple.
    Used to make two way node connection in the graph.

    Args:
        link (tuple): The link of the form (source,target,cost)

    Returns:
        reversed_link (tuple): The reversed link
    """
    reversed_link=(link[1], link[0], link[2])
    return reversed_link


def route_nw_gen() -> nx.DiGraph:
    """
    Generate a directed graph based on the fpga routing architecture.
    All the connections have same weight(=1).

    Returns:
        G (nx.DiGraph): The routing network graph
    """
    ports = ["a", "b", "c", "clk"]

    # The lists to store the tuples of connections
    graph_conns = {
        "port_a": [],
        "port_b": [],
        "port_c": [],
        "port_clk": [],
        "port_io": [],
        "v_sbox": [],
        "h_sbox": [],
        "port_y": [],
        "abc_y": [],
    }

    G = nx.DiGraph()  # Graph object initialisation

    r = cfg.ROWS_CNT
    c = cfg.COLS_CNT

    for port in ports:
        # Connections of port A of CLB
        if port == "a":
            for i in range(r * c):
                for j in range(cfg.ROUTE_CHNL_SIZE):
                    graph_conns[f"port_{port}"].append(
                        (f"v{i//c}{i%c}{j}", f"{port}{i}", cfg.EDGE_COST)
                    )

        # connections of port B of CLB
        elif port == "b":
            for i in range(r * c):
                for j in range(cfg.ROUTE_CHNL_SIZE):
                    graph_conns[f"port_{port}"].append(
                        (f"h{i//c}{i%c}{j}", f"{port}{i}", cfg.EDGE_COST)
                    )

        # connections of port C of CLB
        elif port == "c":
            for i in range(c, (r + 1) * c):  # since port c at the bottom of CLB
                for j in range(cfg.ROUTE_CHNL_SIZE):
                    graph_conns[f"port_{port}"].append(
                        (f"h{i//c}{i%c}{j}", f"{port}{i-c}", cfg.EDGE_COST)
                    )

        # connections of port CLK of CLB
        elif port == "clk":
            for i in range(c, (r + 1) * c):  # since port clk at the bottom of CLB
                for j in range(
                    cfg.ROUTE_CHNL_SIZE - 1
                ):  # -1 because the last channel is not used and is assgined to the main clk
                    graph_conns[f"port_{port}"].append(
                        (f"h{i//c}{i%c}{j}", f"{port}{i-c}", cfg.EDGE_COST)
                    )

    # connections of the io-pins to the routing channels
    gs = cfg.IO_GRP_SIZE
    io_pins_cnt = gs * (2 * (r + c))  # Assuming pins on each outer channel
    for i in range(io_pins_cnt):
        if i < gs * r:
            for j in range(cfg.ROUTE_CHNL_SIZE):
                link = (f"p{i}", f"v{i//gs}0{j}", 1)
                graph_conns["port_io"].append(link)

                # two way connection
                graph_conns["port_io"].append(reverse_link(link))

        elif i < (gs * (r + c)):
            for j in range(cfg.ROUTE_CHNL_SIZE):
                link = (f"p{i}", f"h{r}{(i-(gs*r))//gs}{j}", 1)
                graph_conns["port_io"].append(link)

                # two way connection
                graph_conns["port_io"].append(reverse_link(link))
        elif i < (gs * (2 * r + c)):
            for j in range(cfg.ROUTE_CHNL_SIZE):
                link = (f"p{i}", f"v{(gs*(2*r+c)-(gs-1)-i)//gs}{c}{j}", 1)
                graph_conns["port_io"].append(link)

                # two way connection
                graph_conns["port_io"].append(reverse_link(link))
        else:
            for j in range(cfg.ROUTE_CHNL_SIZE):
                link = (f"p{i}", f"h0{(gs*(2*(r+c))-(gs-1)-i)//gs}{j}", 1)
                graph_conns["port_io"].append(link)

                # two way connection
                graph_conns["port_io"].append(reverse_link(link))

    # connections of the vertical routing channels
    for i in range(r * (c + 1)):
        for j in range(cfg.ROUTE_CHNL_SIZE):
            link1 = (f"v{i//(c+1)}{i%(c+1)}{j}", f"s{i}{j}", 1)
            link2 = (f"v{i//(c+1)}{i%(c+1)}{j}", f"s{i+(c+1)}{j}", 1)
            graph_conns["v_sbox"].append(link1)
            graph_conns["v_sbox"].append(link2)

            # two way connection
            graph_conns["v_sbox"].append(reverse_link(link1))
            graph_conns["v_sbox"].append(reverse_link(link2))

    # connections of the horizontal routing channels
    for i in range((r + 1) * c):
        for j in range(cfg.ROUTE_CHNL_SIZE):
            link1 = (f"h{i//c}{i%c}{j}", f"s{i+(i//c)}{j}", 1)
            link2 = (f"h{i//c}{i%c}{j}", f"s{i+(i//c)+1}{j}", 1)
            graph_conns["h_sbox"].append(link1)
            graph_conns["h_sbox"].append(link2)

            # two way connection
            graph_conns["h_sbox"].append(reverse_link(link1))
            graph_conns["h_sbox"].append(reverse_link(link2))

    # connections of the output of CLB's to the routing channels
    for i in range(r * c):
        for j in range(1, cfg.OUT_CNT + 1):
            for k in range(cfg.ROUTE_CHNL_SIZE):
                graph_conns["port_y"].append((f"y{i}{j}", f"v{i//3}{i%3+1}{k}", 1))

    # # 8888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
    # for i in range(r * c):
    #     for j in range(1, cfg.OUT_CNT):
    #         graph_conns["abc_y"].append(("a" + str(i), "y" + str(i) + str(j), 500))
    #         graph_conns["abc_y"].append(("b" + str(i), "y" + str(i) + str(j), 500))
    #         graph_conns["abc_y"].append(("c" + str(i), "y" + str(i) + str(j), 500))

    # add all the graph connections to the graph object created at the start
    for graph_conn in graph_conns.keys():
        G.add_weighted_edges_from(graph_conns[graph_conn])

    return G


def get_paths_cost(g: nx.DiGraph, codelines: list) -> list[int,list]:
    """
    Generates the shortest path for all the connections in the route_list and along with the total cost.
    Args:
        g (nx.DiGraph): Routing graph
        codelines (list): Generalised code

    Returns:
        cost (int): _description_
        paths (list): _description_
    """

    route_list= conn_list_gen(codelines)
    used_nodes = []  # Contains all the nodes that have been used up
    shorted_nodes = {}  # Contains all the nodes that are shorted
    
    #All the functions below are defined local to get_paths_cost so that used_nodes and shorted_nodes are global and the modified data is accessed by the subfunctions.
    def get_path(graph:nx.DiGraph, source:str, target:str)->Tuple[int,list]:
        """
        Generate the path between source and target using dijkstra's algorithm and return the cost for it.
        Args:
            graph (nx.DiGraph): Routing graph
            source (str): Source node
            target (str): Target node

        Returns:
            cost (int): Cost of the path created
            path (list): Path created
        """
        try:
            cost, path = nx.single_source_dijkstra(graph, source, target)
        except nx.NetworkXNoPath:
            cost = None
            path = None
        return cost, path

    def path_gen(g: nx.DiGraph, connections: list) -> list:
        """
        Generates the shortest path for all the connections in the route_list.

        Args:
            g (nx.DiGraph): Routing graph
            connections (list): (source,target)

        Returns:
            paths (list): The paths for all the routing codes
        """
        paths = []
        for connection in connections:
            # Deepcopy of routing graph required as g will get modifed due to deleted nodes
            graph = copy.deepcopy(g)

            """
            To create the shortest path using shorted nodes(if possible)
            Eg:If path for A --> B is created.[A,v010,h110,B]
            We delete the nodes used from the graph so that they aren't used for other routing connections.
            Now path for B --> C is to be created. it could be possible that the shortest path would be [B,v010,h210,C].
            However this wont be created as the node v010 would have been deleted from the graph. Hence, we restore the shorted nodes to
            take care of this possibility.
            """
            if (connection[0] in shorted_nodes.keys()) and (connection[1] in shorted_nodes.keys()):
                restored_nodes = list(
                    set(shorted_nodes[connection[0]]) | set(shorted_nodes[connection[1]])
                )
            elif connection[0] in shorted_nodes.keys():
                restored_nodes = shorted_nodes[connection[0]]
            elif connection[1] in shorted_nodes.keys():
                restored_nodes = shorted_nodes[connection[1]]
            else:
                restored_nodes = []
                
            graph.remove_nodes_from(list(set(used_nodes) - set(restored_nodes)))
            costs = {}
            
            input_port_pattern='([abc]|(clk))\d'
            #Find the shortest path possible taking the shorted nodes into account
            if connection[0] in shorted_nodes.keys():
                for i in shorted_nodes[connection[0]]:
                    #Not considering the input port nodes as only channel is connected to an input port and if we
                    #consider that here, we might get a path having different channel connected to the port
                    if re.search(input_port_pattern,i):
                        continue
                    
                    if connection[1] in shorted_nodes.keys():
                        for j in shorted_nodes[connection[1]]:
                            if re.search(input_port_pattern,j):
                                continue
                            cost, path = get_path(graph, i, j)
                            if cost:
                                costs[cost] = path
                            #Skip if no path possible 
                            else:
                                continue
                    else:
                        cost, path = get_path(graph, i, connection[1])
                        if cost:
                            costs[cost] = path
                        else:
                            continue
            else:
                if connection[1] in shorted_nodes.keys():
                    for j in shorted_nodes[connection[1]]:
                        if re.search(input_port_pattern,j):
                            continue
                        cost, path = get_path(graph, connection[0], j)
                        if cost:
                            costs[cost] = path
                        else:
                            continue
                else:

                    cost, path = get_path(graph, connection[0], connection[1])
                    if cost:
                        costs[cost] = path
                    else:
                        return None
            
            #Get the path with least cost
            if costs.keys():
                path = costs[min(costs.keys())]
            else:
                return None
            
            #Remove the switch box nodes from the path as they don't need to be deleted 
            sbox_pattern = "[sS]\d\d"
            path_wo_sbox = [node for node in path if not re.search(sbox_pattern, node)]
            paths.append(path)
            for node in path:
                shorted_nodes[node] = path_wo_sbox
                wire_pin_pattern = "([vhVH]\d\d\d)|([Pp]\d{1,2})"
                if re.search(wire_pin_pattern, node):
                    used_nodes.append(node)
        return paths

    paths = path_gen(g, route_list)

    if paths:
        cost = total_cost(paths)
        return [cost, paths]
    else:
        return [None, None]



def total_cost(paths:list)->int:
    """
    Gets the total cost of all the paths in terms of wires and switch boxes.

    Args:
        paths (list): The paths for all the routing codes

    Returns:
        t_cost (int): The total cost of all the paths in terms of wires and switch boxes
    """
    wire_set = set()
    sw_box_set = set()
    pattern_wire = "[VvHh]\d\d\d"
    pattern_sw_box = "[Ss]\d{2,3}"
    for path in paths:
        for node in path:
            result_wire = re.search(pattern_wire, node)
            result_sw_box = re.search(pattern_sw_box, node)
            if result_wire:
                wire_set.add(node)
            if result_sw_box:
                sw_box_set.add(node)

    t_cost = len(wire_set) + len(sw_box_set)

    return t_cost


def conn_list_gen(code_lines: list) ->list:
    """
    Extracts the routing codes out of the generalised codes.

    Args:
        code_lines (list): The generalised code

    Returns:
        route_list (list): Contains tuples of connections, example: [(p0,a0),(y10,p20)]
    """
    route_list = []
    for code in code_lines:
        clb_io_pattern = "(?P<source_pin>(a|b|c|A|B|C|clk|CLK|p|P|y|Y)\d{1,2}) *--> *(?P<target_pin>(a|b|c|A|B|C|clk|CLK|p|P|y|Y)\d{1,2})"

        clb_io_res = re.search(clb_io_pattern, code)

        if clb_io_res:
            route_list.append((clb_io_res.group("source_pin"), clb_io_res.group("target_pin")))

    return route_list


def detailed_code_gen(paths:list[list], clb_list:list[Clb])->list:
    """
    Generates the code of the form "(source) --> (target)" including the routing channels
    and also sets the channel to be selected as the input by the mux's in the CLB.

    Args:
        paths (list[list]): The path list for all the connections
        clb_list (list[Clb]): All the instantiated Clb objects

    Returns:
        codes (list): '(source) --> (target)' with routing channels
    """
    codes = []
    sw_box_pattern = "[sS]\d\d"
    clb_io_pattern = (
        "([VvHh]\d\d(?P<port_no>\d) *--> *(?P<port>a|b|c|A|B|C|clk|CLK)(?P<clb_number>\d))|((?P<port1>a|b|c|A|B|C|clk|CLK)(?P<clb_number1>\d) *--> *[VvHh]\d\d(?P<port_no1>\d))"
    )
    for path in paths:
        pop_list = []
        for i,node in enumerate(path):
            if re.search(sw_box_pattern,node):
                pop_list.append(i)
                
        #Remove the switch boxes
        path = [i for j, i in enumerate(path) if j not in pop_list]

        for i in range(len(path) - 1):
            code = path[i] + " --> " + path[i + 1]
            clb_io_res = re.search(clb_io_pattern, code)
            if clb_io_res:
                #Set the input port that each clb input mux should select
                clb_list[int(clb_io_res.group("clb_number"))].inputs[f"{clb_io_res.group('port').lower()}_no"] = clb_io_res.group("port_no")
                # if clb_io_res.group("clb_number"):
                #     clb_list[int(clb_io_res.group("clb_number"))].inputs[f"{clb_io_res.group('port').lower()}_no"] = clb_io_res.group("port_no")
                # else:
                #     clb_list[int(clb_io_res.group("clb_number1"))].inputs[f"{clb_io_res.group('port1').lower()}_no"] = clb_io_res.group("port_no1")
            else:
                codes.append(code)
    return codes

