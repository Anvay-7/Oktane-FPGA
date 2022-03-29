class Placer():
    def __init__(self):
        clb_links=[(0,1),(1,2),(3,4),(4,5),(6,7),(7,8),(0,3),(3,6),(1,4),(4,7),(2,5),(5,8)]
        self.graph=nx.Graph()
        self.graph.add_edges_from(clb_links)

        self.logic_func={}
        self.code_del_list=[]
        self.port_assign_code=[]
        self.func_inputs={}
        self.clb_0_8=[0,1,2,3,4,5,6,7,8]

    @staticmethod
    def extract_vars(code):
        pattern='\w+'
        input_list=re.findall(pattern,code)
        input_list=list(dict.fromkeys(input_list))
        input_list_len=len(input_list)
        io_dict={}
        io_dict['y']=input_list[0]
        io_dict['a']=input_list[1]
        io_dict['b']=input_list[2] if input_list_len>=3 else ''
        io_dict['c']=input_list[3] if input_list_len==4 else ''
        # io_dict['op12']=res.group('op12') if res.group('op12') else ''
        # io_dict['op23']=res.group('op23') if res.group('op23') else ''
        #input_del_list=[io_dict['y']]
        #inputs=[j for i,j in enumerate(list(io_dict.values())) if j not in input_del_list ]
        inputs=list(io_dict.values())
        inputs.pop(0)
        #print(colors.fg.orange,inputs,colors.reset)
        #print(io_dict,inputs)
        return io_dict,inputs

    @staticmethod
    def stop_condition(lst):
        if len(lst)>cnst.K:
            least=np.min(lst)
            av=np.mean(lst[-cnst.K:])
            flag= 0 if av == least else 1
            return flag
        return 1


    def add_clb_no(code,io_dict,state,new_code_lines,updated_port_assign_code,io_port_conn):
        clb_no=state[0]
        y_no=state[1]
        #updated_port_assign_code=copy.deepcopy(port_assign_code)
        new_code=''
        for key,val in io_dict.items():
            if val:
                
                if val in io_port_conn.keys():
                    new_code_lines.append(io_port_conn[val]+' --> '+key+str(clb_no))
                for i,port_code in enumerate(updated_port_assign_code):
                    pattern='(?P<port>[Pp]\d{1,2})'
                    res=re.search(pattern,port_code)
                    pattern_input='\\b'+val+'\\b'
                    res_input=re.search(pattern_input,port_code)
                    if key=='y':
                        code=code.replace(val,key+str(clb_no)+str(y_no))
                        if res and res_input:
                            io_port_conn[val]=key+str(clb_no)+str(y_no)
                        updated_port_assign_code[i]=updated_port_assign_code[i].replace(val,key+str(clb_no)+str(y_no))
                    elif key in ['a','b','c']:
                        code=code.replace(val,key)
                        if res and res_input:
                            io_port_conn[val]=res.group('port')
                        updated_port_assign_code[i]=updated_port_assign_code[i].replace(val,key+str(clb_no))
                
                if val not in io_port_conn.keys():
                    io_port_conn[val]=key+str(clb_no)+str(y_no)
                    
        new_code=code

        return new_code,updated_port_assign_code


    def gen_code(self,reduced_code_lines):
        new_code_lines=[]
        self.curr_state={}
        self.io_port_conn={}
        updated_port_assign_code=copy.deepcopy(self.port_assign_code)
        for code in self.logic_func.keys():
            curr_state[code]=self.logic_func[code][1]
            self.logic_func[code][2],updated_port_assign_code=add_clb_no(code,self.logic_func[code][0],self.curr_state[code],new_code_lines,updated_port_assign_code,self.io_port_conn)
            new_code_lines.append(self.logic_func[code][2])
        updated_code_lines=copy.deepcopy(reduced_code_lines)
        new_code_lines.extend(updated_port_assign_code)
        updated_code_lines.extend(new_code_lines)
        #print('io_port_conn----> ',io_port_conn)

        return updated_code_lines,self.curr_state


    def initial_state_gen(self,code_lines):
        for i,code in enumerate(code_lines):
            #pattern1='(?P<y>\w+) *(?P<sync_async><?)= *[\(\s\)]*(?P<not1>~?)(?P<a>[\(\s\)]*[a-zA-Z0-9]+) *((?P<op12>[-^&|]) *[\(\s\)]*(?P<not2>~?)[\(\s\)]*(?P<b>[a-zA-Z0-9]+))? *((?P<op23>[-^&|]) *[\(\s\)]*(?P<not3>~?)[\(\s\)]*(?P<c>[a-zA-Z0-9]+)[\(\s\)]*)?'
            logic_expr_pattern='(?P<y>\w+) *(?P<async_sync><?)=' 
            conn_pattern='([Pp]\d{1,2} *--> *(?P<var_in>[a-zA-Z0-9]+))|((?P<var_out>[a-zA-Z0-9]+) *--> *[Pp]\d{1,2})'
            #print(logic_expr_pattern)
            logic_expr_result=re.search(logic_expr_pattern,code)
            conn_result=re.search(conn_pattern,code)
            #random_initialisation
            if logic_expr_result:
                self.code_del_list.append(i)
                ini_clb_no=random.choice(self.clb_0_8)
                ini_y_no=random.randint(1,2)
                self.clb_0_8.remove(ini_clb_no)
                func_dict,self.func_inputs[code]=self.extract_vars(code)
                self.logic_func[code]=[func_dict,(ini_clb_no,ini_y_no,),'']
            if conn_result:
                self.code_del_list.append(i)
                self.port_assign_code.append(code)    

            reduced_code_lines=[j for i,j in enumerate(code_lines) if i not in self.code_del_list ]
            
            self.curr_state_code_lines,self.curr_state =  self.gen_code(reduced_code_lines)
        return self.curr_state

    def sim_anneal(self,reduced_code_lines):
        cost_list=[]
        curr_cost=get_cost(self.curr_state_code_lines)
        i=0
        temp=cnst.INI_TEMP
        while (self.stop_condition(cost_list)):
            i+=1
            #print(curr_cost)

            cost_list.append(curr_cost[0])
            #print(colored(' COST ','magenta','on_white'),colored(curr_cost,'magenta'))

            new_states=next_state(self.graph,curr_state)
            #print(colored(' NEW STATE ','yellow','on_blue',['bold']),colored(new_states,'yellow'))

            next_state_code_lines,_=gen_code(reduced_code_lines)
            #print(colored(' CODE LINES ','green','on_red',['bold']),colored(next_state_code_lines,'green'))
            new_cost=get_cost(next_state_code_lines)
            delta=new_cost[0]-curr_cost[0]
            #cost_list.append(delta)
            #print(colored('  DELTA ','magenta','on_white'),colored(delta,'magenta'))
        
            if delta<=0:
                curr_state=new_states
                curr_state_code_lines=next_state_code_lines
                curr_cost=new_cost
                
            else:
                threshold=random.uniform(0,1)
                probability=math.exp(-(delta/temp))
                print(probability, temp)
                if threshold<probability:
                    curr_state=new_states
                    curr_state_code_lines=next_state_code_lines
                    curr_cost=new_cost
                else:
                    for code in self.logic_func.keys():
                        self.logic_func[code][1]=curr_state[code]
            temp*=cnst.FACTOR