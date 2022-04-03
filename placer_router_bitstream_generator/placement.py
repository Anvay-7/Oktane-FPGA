import random
import numpy as np
from termcolor import colored
import networkx as nx
import copy
import math
import re
from typing import Tuple
import config as cfg
from graph_nw import get_paths_cost
from statistics import stdev


def extract_vars(expr:str,clk:str)->Tuple[dict,list]:
    """
    Extract the variables and assign to respective attributes.

    Args:
        expr (str): example =  'sum_0 <=input1_0^input2_0'
        clk (str): The clock variable if present

    Returns:
        io_dict (dict): example = {'y': 'sum_0', 'a': 'input1_0', 'b': 'input2_0', 'c': ''}
        inputs (list): All the inputs in the expression(no duplicates).
                       example = ['input1_0', 'input2_0', '']
    """
    io_dict={}
    if clk:
        io_dict['clk']=clk
    
    #Get all the variables in the expression   
    pattern='\w+'
    vars_list=re.findall(pattern,expr)
    
    #Remove any duplicates
    vars_list=[vars_list[0]] + list(dict.fromkeys(vars_list[1:]))
        
    io_dict['y']=vars_list[0]
    io_dict['a']=vars_list[1]
    io_dict['b']=vars_list[2] if len(vars_list)>=3 else ''
    io_dict['c']=vars_list[3] if len(vars_list)==4 else ''
    
    #Remove the output('y') variable
    if clk:
        vars_list.pop(1)
    else:
        vars_list.pop(0)
    inputs=vars_list
        
    return io_dict,inputs


def add_clb_no(expr:str,expressions:dict,state:tuple,new_code_lines:list,copy_routing_codes:list,io_port_conn:dict,clk_dict:dict)->Tuple[str,list]:
    """
    Creates the generalised code in terms of port notations.

    Args:
        expr (str): 'sum_0 <=input1_0^input2_0'
        expressions (dict): Contains expression:[io_dict,state,converted expr,clk_var]
        state (tuple): (clb_no,y_no)
        new_code_lines (list): the code lines having port names instead of variables
        copy_routing_codes (list): All the routing codes with variables
        io_port_conn (dict): Stores the ports assigned to the io variables
        clk_dict (dict): Stores the ports assigned to the clk variables

    Returns:
        expr (str): converted generalised expression
        copy_routing_codes (list): partially converted routing codes until all the expressions have been passed through thois fucntion
    """
    io_dict=expressions[expr][0]
    clb_no,y_no=state
    new_clk_conns=[]
    clk_flag=1
    
    for key,val in io_dict.items():
        if val:
            #If var1 --> var2 and a0 --> var1 then modify the code to a0 -->var2. This is done by storing the ports of variables in io_port_conn             
            if val in io_port_conn.keys():
                if key=='y':
                    new_code_lines.append(f"{key}{clb_no}{y_no} --> {io_port_conn[val]}")
                else:
                    new_code_lines.append(f"{io_port_conn[val]} --> {key}{clb_no}")
                
            #Replace the variable with the port in the expression and the routing codes      
            for i,route_code in enumerate(copy_routing_codes):
                pattern='(?P<port>[Pp]\d{1,2})'
                res_pin=re.search(pattern,route_code)
                pattern_input=fr"\b{val}\b"
                res_input=re.search(pattern_input,route_code)
                if key=='y':
                    #Done so that only the output gets replaced (eg. q0 <= q0 to y01 <= q0)
                    if re.search(fr"\b{val}\b *!?<?=",expr):
                        expr=re.sub(fr"\b{val}\b",f"{key}{clb_no}{y_no}",expr,count=1)
                        #expr=expr.replace(val,f"{key}{clb_no}{y_no}",1) # Only one replacement
                        
                    if res_pin and res_input:
                        io_port_conn[val]=f"{key}{clb_no}{y_no}"
                    copy_routing_codes[i]=re.sub(fr"\b{val}\b",key+str(clb_no)+str(y_no),copy_routing_codes[i])
                    #copy_routing_codes[i]=copy_routing_codes[i].replace(val,key+str(clb_no)+str(y_no))
                elif key in ['a','b','c']:
                    expr=re.sub(fr"\b{val}\b",key,expr)
                    #expr=expr.replace(val,key)
                    if res_pin and res_input:
                        io_port_conn[val]=res_pin.group('port')
                    copy_routing_codes[i]=re.sub(fr"\b{val}\b",key+str(clb_no),copy_routing_codes[i])
                    #copy_routing_codes[i]=copy_routing_codes[i].replace(val,key+str(clb_no))
                    
                    #Since routing graph is directed graph, path from [a,b,c] to something else isn't possible. So reverse the connection.
                    input_port_pattern='(?P<input>([abc]|(clk))\d) *--> *(?P<port>p\d{1,2})'
                    input_port_result = re.search(input_port_pattern,copy_routing_codes[i])
                    if input_port_result:
                        copy_routing_codes[i]=f"{input_port_result.group('port')} --> {input_port_result.group('input')}"

                elif key =='clk':
                    #To add clk connection to all the CLB's if same clk is connected to multiple CLB's
                    if clk_dict.get(val) and clk_flag:
                        new_clk_conns.append(f"{clk_dict[val]} --> clk{clb_no}")
                        clk_flag=0
                        
                    #Stores the port the clock is connected to    
                    if res_pin and res_input:
                        clk_dict[val]=res_pin.group('port')
                        
                    split_pattern='(?P<g1>\w+ *!?<)(?P<g2>.+)'
                    split_res=re.search(split_pattern,expr)
                    if expressions.get(expr):
                        if clk_dict.get(expressions[expr][3]):
                            #Add the port number in the expression 
                            expr=split_res.group('g1')+clk_dict[expressions[expr][3]]+split_res.group('g2')
                    copy_routing_codes[i]=re.sub(fr"\b{val}\b",'clk'+str(clb_no),copy_routing_codes[i])
                    #copy_routing_codes[i]=copy_routing_codes[i].replace(val,'clk'+str(clb_no))
            
            #Add the variable which is connected only internally and not to any of the external io ports
            if val not in io_port_conn.keys():
                if key!='clk':
                    io_port_conn[val]=key+str(clb_no)+str(y_no)
                
    return expr,copy_routing_codes


def next_state(graph:nx.Graph,curr_state:dict,expressions:dict,expr_inputs:dict)->dict:
    """
    Generates the next state of the expression by assigning it to a new CLB
    during which the another expression may or may not get swapped as an effect of it.
    In some cases no change occurs.

    Args:
        graph (nx.Graph): CLB network graph
        states (dict): The assigned (clb_no,y_no) to each expression
        expressions (dict): Contains the details about each expression
        expr_inputs (dict): All the inputs in each expression(no duplicates).

    Returns:
        states (dict): The newly assigned (clb_no,y_no) to each expression
    """
    states=copy.deepcopy(curr_state)
    #Select an expression randomly
    expr_swapped=random.choice(list(states.keys()))    
    old_state=states[expr_swapped]
    
    #Choose a random adjacent CLB
    clb_no=random.choice(list(graph.neighbors(old_state[0])))

    y_no=random.randint(1,2)
    new_state=(clb_no,y_no)
    
    #All the occupied CLB's at the moment
    occupied_clb_list=[clb_no for clb_no,_ in list(states.values())]
    
    clb_match_count=occupied_clb_list.count(new_state[0])
    
    #If the new CLB selected is not occupied by any other expression
    if clb_match_count==0:
        states[expr_swapped]=new_state
        expressions[expr_swapped][1]=states[expr_swapped]
        return states
    else:
        for expr,occupied_state in states.items():
            if new_state[0]==occupied_state[0]: #If same CLB 
                if clb_match_count>=2:
                    """
                    Swap CLB's only if the inputs of the two expressions match.
                    Example: CLB1 has two expressions(expr1 and expr2). Therefore, we can conclude that both the expressions have the same inputs.
                    Suppose, a different expression(say expr3) is chosen to be swapped with expr1, it is necessary for expr3 to have
                    same inputs as that of expr1, in order to be compatible with expr2.
                    """ 
                    if chk_same_inputs(expr_inputs,expr_swapped,expr):
                        states[expr]=old_state
                        expressions[expr][1]=states[expr]

                        states[expr_swapped]=new_state
                        expressions[expr_swapped][1]=states[expr_swapped]
                        return states
                    else:
                        #Do not swap if the inputs dont match
                        return states
                
                """
                If the new CLB is occupied by only 1 expression.
                We can add the expression to be swapped into the vacant position if and only if the inputs of the 
                exisying expression and swapped expression match
                """
                if chk_same_inputs(expr_inputs,expr_swapped,expr):
                    if occupied_state[1]==1:
                        new_y_no=2
                    else:
                        new_y_no=1
                    states[expr_swapped]=(new_state[0],new_y_no)
                    expressions[expr_swapped][1]=states[expr_swapped]
                    return states
                else:
                    """
                    If the CLB assigned to swapped expression has only a single expression assigned to it(i.e the swapped expr),
                    then swap the expressions.           
                    """    
                    if occupied_clb_list.count(old_state[0])<2:
                        states[expr]=old_state
                        expressions[expr][1]=states[expr]

                        states[expr_swapped]=new_state
                        expressions[expr_swapped][1]=states[expr_swapped]
                        return states
                    else:
                        #Do not swap
                        return states

    


def chk_same_inputs(expr_inputs:dict,expr1:str,expr2:str)->bool:
    """
    Checks whether the two expressions have same input or not.

    Args:
        expr_inputs (dict): All the inputs in each expression(no duplicates).
        expr1 (str): expression1
        expr2 (str): expression2

    Returns:
        flag (bool): Whether the two expressions have same input or not
    """
    flag=True
    for input in expr_inputs[expr1]:
        if input not in expr_inputs[expr2]:
            flag=False

    return flag

def gen_code(expressions:dict,routing_codes:list)->Tuple[list,dict,list]:
    """
    Generate generalised code from AHDL7.

    Args:
        expressions (dict): Contains the details about each expression
        routing_codes (list): Port connection codes in AHDL7

    Returns:
        new_code_lines (list): The generalised code
        curr_state (dict): The expressions with the assigned CLB and output number
        converted_exprs (list): The generalised expressions
    """
    new_code_lines=[]
    curr_state={}
    io_port_conn={}
    clk_dict={}
    converted_exprs=[]
    # Make a deepcopy of the routing codes as we generate the generalised routing codes from this every iteration. Hence we do not want to modify this list
    copy_routing_codes=copy.deepcopy(routing_codes)
    for expr in expressions.keys():
        curr_state[expr]=expressions[expr][1] #(clb_no,y_no)
        expressions[expr][2],copy_routing_codes=add_clb_no(expr,expressions,curr_state[expr],new_code_lines,copy_routing_codes,io_port_conn,clk_dict)
        new_code_lines.append(expressions[expr][2])
        converted_exprs.append(expressions[expr][2])
        
    new_code_lines.extend(copy_routing_codes)

    return new_code_lines,curr_state,converted_exprs

def stop_condition(costs:list)->int:
    """
    Decides whether to stop the simulated annealing process or not.

    Args:
        costs (list): The costs of all the iterations prior to the current one.

    Returns:
        int: 0(stop) or 1(continue)
    """
    k=cfg.K
    if len(costs)>k:
    #     least=np.min(costs)
    #     av=np.mean(costs[-k:])
    #     flag= 0 if av == least else 1
    #     return flag
        if np.mean(costs[-k:])==costs[-1:][0]:
            return 0
    return 1

def clb_nw_gen()->nx.Graph:
    """
    Generate a undirected graph based on the CLB network.

    Returns:
        nx.Graph: The CLB network graph
    """
    clb_links=[(0,1),(1,2),(3,4),(4,5),(6,7),(7,8),(0,3),(3,6),(1,4),(4,7),(2,5),(5,8)]
    clb_conn_graph=nx.Graph()
    clb_conn_graph.add_edges_from(clb_links)
    return clb_conn_graph

def placer(route_nw:nx.DiGraph,clb_nw:nx.Graph,code_lines:list)->Tuple[list,int,list]:
    """
    _summary_

    Args:
        route_nw (nx.DiGraph): The routing network graph
        clb_nw (nx.Graph): The CLB network graph
        code_lines (list): examples =  'p0 --> input1_0', 'sum_0 <=input1_0^input2_0'

    Returns:
        curr_state_code_lines (list): The generalised code
        curr_cost_path[1] (int): The path list for all the connections
        converted_exprs (list): The generalised expressions
    """
    code_del_list=[]
    clb_0_8=[0,1,2,3,4,5,6,7,8]
    routing_codes=[]
    expressions={}
    expr_inputs={}
    
    for i,code in enumerate(code_lines):
        expr_pattern='(?P<y>\w+) *(?P<ff_edge>!?)(?P<async_sync><?)(?P<clock>\w*)='
        conn_pattern='([Pp]\d{1,2} *--> *(?P<var_in>[a-zA-Z0-9]+))|((?P<var_out>[a-zA-Z0-9]+) *--> *[Pp]\d{1,2})'
        
        #Check if logic expression code
        expr_result=re.search(expr_pattern,code)
        
        #Check if port connection code
        conn_result=re.search(conn_pattern,code)
        
        #random_initialisation
        if expr_result:
            code_del_list.append(i)
            
            #Remove the clock variable from the expression
            #example: 'a <foo= b&c' changed to 'a <= b&c'
            expr=code.replace(expr_result.group('clock'),'') 
            
            ini_clb_no=random.choice(clb_0_8)
            ini_y_no=random.randint(1,2)
            
            #Remove the clb number so that it doesn't get selected for any other expression
            clb_0_8.remove(ini_clb_no)
            
            expr_dict,expr_inputs[expr]=extract_vars(expr,expr_result.group('clock'))
            
            #Converting None to ''
            clock_var=expr_result.group('clock') or ''
            
            expressions[expr]=[expr_dict,(ini_clb_no,ini_y_no,),'',clock_var]
        if conn_result:
            code_del_list.append(i)
            routing_codes.append(code)
    
    print(colored(' LOGIC FUNC ','grey','on_green',['bold']),colored(expressions,'cyan')) 
    print(colored(' PORT ASSIGN CODE ','white','on_red',['bold']),colored(routing_codes,'magenta'))

    cost_list=[]
    curr_state_code_lines,curr_state,curr_conv_exprs=gen_code(expressions,routing_codes)
    initial_state=copy.deepcopy(curr_state) #⚠️⚠️⚠️⚠️⚠️⚠️⚠️no need of deepcopy if initial state is not needed at the end
    
    print(colored(initial_state,"blue"))
    print(colored(' CURRENT STATE ','yellow','on_blue',['bold']),colored(curr_state,'yellow'))
    print(colored(' CODE LINES ','green','on_red',['bold']),colored(curr_state_code_lines,'green'))
    
    curr_cost_path=get_paths_cost(route_nw,curr_state_code_lines)
    print(curr_cost_path[1])
    temperature=cfg.INI_TEMP
    
    delta_list=[]
    
    i=0
    while (stop_condition(cost_list)):
    #while(i<100):
        i+=1
        
        print("Iteration -- ", i)
        
        if curr_cost_path[0]:
            cost_list.append(curr_cost_path[0])
            print(i,colored(curr_cost_path[0],'magenta'))
        #print(colored(' COST ','magenta','on_white'),colored(curr_cost,'magenta'))

        new_states=next_state(clb_nw,curr_state,expressions,expr_inputs)
        #print(colored(' NEW STATE ','yellow','on_blue',['bold']),colored(new_states,'yellow'))

        next_state_code_lines,_,new_conv_exprs=gen_code(expressions,routing_codes)
        #print(colored(' CODE LINES ','green','on_red',['bold']),colored(next_state_code_lines,'green'))
        new_cost_path=get_paths_cost(route_nw,next_state_code_lines)
        
        #Skip if the path doesn't exist for new state generated
        if new_cost_path[0]==None:
            #Revert back to previous state since no solution possible for new state
            for code in expressions.keys():
                    expressions[code][1]=curr_state[code]
            continue
        
        if curr_cost_path[0]:
            delta=new_cost_path[0]-curr_cost_path[0]
        #To account for the case when the path for initial state doesn't exist(curr_cost_path would be None in that case)
        else:
            delta=0
        #delta=new_cost_path[0]-curr_cost_path[0]
        #cost_list.append(delta)
        #print(colored('  DELTA ','magenta','on_white'),colored(delta,'magenta'))
    
        #Always accept the good move
        if delta<=0:
            curr_state=new_states
            curr_state_code_lines=next_state_code_lines
            curr_cost_path=new_cost_path  
            curr_conv_exprs=new_conv_exprs
        else:
            threshold=random.uniform(0,1)
            probability=math.exp(-(delta/temperature))
            print('           '+colored(probability,'green'))
            
            #Accept the bad move  
            if threshold<probability:
                curr_state=new_states
                curr_state_code_lines=next_state_code_lines
                curr_cost_path=new_cost_path
                curr_conv_exprs=new_conv_exprs
                
            #Reject the bad move
            else:
                for code in expressions.keys():
                    expressions[code][1]=curr_state[code]
        
        # delta_list.append(abs(delta))
        # curr_state=new_states
        # curr_state_code_lines=next_state_code_lines
        # curr_cost_path=new_cost_path  
        # curr_conv_exprs=new_conv_exprs
        
        
        
        temperature=cfg.INI_TEMP*(cfg.FACTOR**i)
        #temperature=cfg.INI_TEMP/math.log(1+i)
    
    # delta_mean=sum(delta_list)/len(delta_list)
    # print(delta_mean)
    
    # t0=(delta_mean+3*statistics.stdev(delta_list))/math.log(1/0.95)
    # print("t0========",t0)
    #print(' DELTA LIST ',cost_list)
    k_counter={}
    cost_set=set(cost_list)
    for cost in cost_set:
        k_counter[cost]=cost_list.count(cost)
    sorted_k_count=dict(sorted(k_counter.items(), key=lambda item: item[1],reverse=True))
    # print(len(cost_list))
    print(sorted_k_count)
    # print(curr_state_code_lines)
    print('no of iterations = ', i)
    # print(initial_state)

    return curr_state_code_lines,curr_cost_path[1],curr_conv_exprs


