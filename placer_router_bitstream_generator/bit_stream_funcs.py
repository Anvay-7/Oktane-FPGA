import re
import config as cfg

class Clb():
    """
    Contains all the data and methods for the usage of CLB.
    """

    def __init__(self,number:int):
        """
        Initialise all the attribute sto their default values.

        Args:
            number (int): The CLB number
        """
        
        self.number=number

        self.inputs={'a_no':None,'b_no':None,'c_no':None,'clk_no':None}
        self.bitstream={
            'clk':'11',
            'port_c':'00',
            'port_b':'00',
            'port_a':'00',
            'as_1':'0',
            'as_2':'0',
            'o_en1':'0',
            'o_en2':'0',
            'ff_edge1':'0',
            'ff_edge2':'0',
            'a_used':'0',
            'b_used':'0',
            'c_used':'0',
            'data1':'{:08b}'.format(0),
            'data2':'{:08b}'.format(0)
        }

        self.data='{0:033b}'.format(0)
        self.exprs={
            'y1':{
                'expr':'',
                'vars':{},
                'var_count':0
            },
            'y2':{
                'expr':'',
                'vars':{},
                'var_count':0
            }
        }

    @staticmethod
    def count_inputs(expr_rhs:str)->tuple[int,dict]:
        """
        Counts the number of input variables in the expression.

        Args:
            expr_rhs (str): The RHS of the generalised expression

        Returns:
            var_count (int): Number of inputs
            input_vars (dict): The input variables along with the assigned index
        """

        word_pattern='\w+'
        input_list=re.findall(word_pattern,expr_rhs)
        
        #Remove duplicates
        input_list=list(dict.fromkeys(input_list))
        
        input_vars={}
        for i,input in enumerate(input_list):
            input_vars[input]=i+1 #To start count from 1
        var_count=len(input_vars)

        return var_count,input_vars

    @staticmethod
    def truth_table(expr_rhs:str,var_count:int,input_vars:dict)->str:
        """
        Generates the truth table for the given expr_rhs.

        Args:
            expr_rhs (str): The RHS of the generalised expression.
            var_count (int): Number of inputs
            input_vars (dict): The input variables along with the assigned index

        Returns:
            outputs (str): The truth table output bits
        """
        #To evaluate the logic expression only for combinations where the unused variable is constant at 0
        
        #Note:"[*dict]" gives the list of keys in the dict
        if var_count==1:
            if [*input_vars][0]=='a':
                const='b|c'
            elif [*input_vars][0]=='b':
                const='a|c'
            else:
                const='a|b'
        elif var_count==2:
            var_set={[*input_vars][0],[*input_vars][1]} #Using set to remove duplicates
            if 'a' in var_set and 'b' in var_set:
                const='c'
            elif 'a' in var_set and 'c' in var_set:
                const='b'
            else:
                const='a'
        else:
            const='0'

        outputs=['0' for _ in range(8)] #Default value of outputs of the truth table
        i=0
        for a in range(2):                  #var1
            for b in range(2):              #var2
                for c in range(2):          #var3
                    if eval(const)==0:
                        value=eval(expr_rhs)
                        outputs[i]=str(value*1)
                    i=i+1
        outputs=''.join(outputs)
        return outputs

    def clb_bitstream_gen(self,expr:str,mode:int,result:re.Match)->None:
        """
        Generate the bitstreamn for the CLB according to the expression.
        
        Args:
            expr (str): Generalised expression
            mode (int): Automatic(1) or manual(2)
            result (re.Match): Match object for clb_pattern
        """
        y_no='y'+result.group('y_no')

        self.exprs[y_no]['expr']=re.sub('[yY]\d\d *!?<?\w*= *','',expr)
        self.exprs[y_no]['expr']=re.sub('~',' not ',self.exprs[y_no]['expr'])

        self.exprs[y_no]['var_count'],self.exprs[y_no]['vars']=self.count_inputs(self.exprs[y_no]['expr'])
        
        a_no=self.inputs['a_no']
        b_no=self.inputs['b_no']
        c_no=self.inputs['c_no']
        clk_no=self.inputs['clk_no']

        #Set the enable for all the input ports being used
        #y
        for var in self.exprs[y_no]['vars'].keys():
            self.bitstream[var+'_used']='1'


        #Set the clock number if custom clock variable is used
        if clk_no:
            self.bitstream['clk']=bin(int(clk_no)).replace('0b','').zfill(2)

        #input C
        if 'c' in self.exprs[y_no]['vars']:
            self.bitstream['port_c']=bin(int(c_no)).replace('0b','').zfill(2)

        #input B
        if 'b' in self.exprs[y_no]['vars']:
            self.bitstream['port_b']=bin(int(b_no)).replace('0b','').zfill(2)

        #input A
        if 'a' in self.exprs[y_no]['vars']:
            self.bitstream['port_a']=bin(int(a_no)).replace('0b','').zfill(2)

        if result.group('y_no')=='1':
            self.bitstream['o_en1']='1'
            if result.group('async_sync'):
                self.bitstream['as_1']='1'
        elif result.group('y_no')=='2':
            self.bitstream['o_en2']='1'
            if result.group('async_sync'):
                self.bitstream['as_2']='1'
                
        #pos or negedge
        if result.group('ff_edge'):
            self.bitstream['ff_edge'+result.group('y_no')]='1'

        #data
        self.bitstream['data'+result.group('y_no')]=self.truth_table(self.exprs[y_no]['expr'],self.exprs[y_no]['var_count'],self.exprs[y_no]['vars'])[::-1]
        
        clb_data_vals=list(self.bitstream.values()) #concatenate the bits
        
        #insert each data field in reverse order (Note: The bits are not reversed inside the data field)
        self.data=''
        for i in range(len(clb_data_vals)-1,-1,-1):
            self.data=self.data+clb_data_vals[i]

def switch_box_bitstream(result:re.Match,switch_box_config:dict)->tuple[str,str]:
    """
    Generates the bitstream for the switch boxes.
    value = (first digit)*4 + (second_digit)

    Args:
        result (re.Match): Match object for switch_box_pattern
        switch_box_config (dict): Bitstream for switch boxes. eg {'s0':'010010'}

    Returns:
        switch_code (str): Switch box bitstream
        switch_no (str): Selected switch box 
    """
    switch_code=0
    switch_no=0
    
    #s3
    if result.group('row1')+result.group('col1')==result.group('row2')+result.group('col2'):
        switch_code=bin(switch_code | 8).replace('0b','').zfill(6)
        switch_no='s'+str(int(result.group('row1'))*4 + int(result.group('col1')))+result.group('layer1') #H_value

    #s1
    elif abs(int(result.group('row1'))-int(result.group('row2')))==abs(int(result.group('col1'))-int(result.group('col2'))):
        switch_code=bin(switch_code| 32).replace('0b','').zfill(6)
        switch_no='s'+str(max(int(result.group('row1')),int(result.group('row2')))*4 + min(int(result.group('col1')),int(result.group('col2')))+ 1)+result.group('layer1') #H_value+1
    
    elif result.group('col1')==result.group('col2'):
        if result.group('pos1').lower()==result.group('pos2').lower():
            #s6
            if abs(int(result.group('row1')+result.group('col1'))-int(result.group('row2')+result.group('col2')))==10 and result.group('pos1').lower()=='v':
                switch_code=bin(switch_code | 1).replace('0b','').zfill(6)
                switch_no='s'+str(max(int(result.group('row1')),int(result.group('row2')))*4 + int(result.group('col1')))+result.group('layer1') #max(V_value1,V_value2)
            else:
                print('Value wrong for V<-->V')
        else:
            #s2
            switch_code=bin(switch_code | 16).replace('0b','').zfill(6)
            switch_no='s'+str(max(int(result.group('row1')),int(result.group('row2')))*4 + int(result.group('col1')))+result.group('layer1') #H_value
    
    elif result.group('row1')==result.group('row2'):
        if result.group('pos1').lower()==result.group('pos2').lower():
            #s5
            if abs(int(result.group('row1')+result.group('col1'))-int(result.group('row2')+result.group('col2')))==1 and result.group('pos1').lower()=='h':
                switch_code=bin(switch_code | 2).replace('0b','').zfill(6)
                switch_no='s'+str(int(result.group('row1'))*4 + max(int(result.group('col1')),int(result.group('col2'))))+result.group('layer1') #max(H_value1,H_value2)
            else:
                print('Value wrong for H<-->H')
        else:
            #s4
            switch_code=bin(switch_code | 4).replace('0b','').zfill(6)
            switch_no='s'+str(int(result.group('row1'))*4 + max(int(result.group('col1')),int(result.group('col2'))))+result.group('layer1') #V_value
    else:
        print('switch code is wrong :(')
    
    switch_box_config[switch_no]=bin(int(switch_box_config[switch_no],2)|int(switch_code,2)).replace('0b','').zfill(6) #updating the switch_code

    return switch_code,switch_no


def io_conn_box_bitstream(result:re.Match,conn_box_config:dict):
    """
    Generates the bitstream for the connection boxes connecting to the io pins.

    Args:
        result (re.Match): Match object for io_conn_box_pattern
        conn_box_config (dict): Bitstream for connection boxes. eg {'c0':'0100'}
    """
    if result.group('pin_r_no'):
        pin_no=result.group('pin_r_no')
    else:
        pin_no=result.group('pin_l_no')

    if result.group('layer_l_no'):
        layer_no=result.group('layer_l_no')
    else:
        layer_no=result.group('layer_r_no')

    if int(pin_no)<=cfg.IO_GRP_SIZE*(cfg.ROWS_CNT+cfg.COLS_CNT)-1:
        conn_code=bin(int(conn_box_config['c'+pin_no],2)|pow(2,(int(layer_no)))).replace('0b','').zfill(4)
    else:
        conn_code=bin(int(conn_box_config['c'+pin_no],2)|pow(2,(3-int(layer_no)))).replace('0b','').zfill(4)

    conn_box_config['c'+pin_no]=bin(int(conn_box_config['c'+pin_no],2)|int(conn_code,2)).replace('0b','').zfill(4)

def clb_conn_box_bitstream(result:re.Match,conn_box_config:dict):
    """
    Generates the bitstream for the connextion boxes connecting to the CLB's.
    
    Args:
        result (re.Match): Match object for clb_conn_box_pattern
        conn_box_config (dict): Bitstream for connection boxes. eg {'c0':'0100'}
    """
    conn_code=bin(int(conn_box_config['c'+str(23+int(result.group('clb_number'))*2+int(result.group('output_no')))])|pow(2,(int(result.group('layer_no'))))).replace('0b','').zfill(4)

    conn_box_config['c'+str(23+int(result.group('clb_number'))*2+int(result.group('output_no')))]=bin(int(conn_box_config['c'+str(23+int(result.group('clb_number'))*2+int(result.group('output_no')))],2)|int(conn_code,2)).replace('0b','').zfill(4)

def bit_stream_config_gen(codes:list,exprs:list,mode:int,clb_list:list[Clb],cbox_data:dict,sbox_data:dict):
    """
    Transfers code to appropriate bitstream generator.

    Args:
        codes (list): '(source) --> (target)' with routing channels
        exprs (list): The generalised expressions
        mode (int): Automatic(1) or manual(2)
        clb_list (list[Clb]): All the instantiated Clb objects
        cbox_data (dict): Bitstream for connection boxes. eg {'c0':'0100'}
        sbox_data (dict): Bitstream for switch boxes. eg {'s0':'010010'}
    """
    io_conn_box_pattern="([Pp](?P<pin_l_no>\d{1,2}) *--> *[vVHh]\d\d(?P<layer_r_no>\d))|([vVHh]\d\d(?P<layer_l_no>\d) *--> *[Pp](?P<pin_r_no>\d{1,2}))"
    clb_conn_box_pattern="[Y|y](?P<clb_number>\d)(?P<output_no>\d) *--> *[vVhH]\d\d(?P<layer_no>\d)"
    switch_box_pattern='(?P<pos1>[H|h|V|v])(?P<row1>\d)(?P<col1>\d)(?P<layer1>\d) *--> *(?P<pos2>[H|h|V|v])(?P<row2>\d)(?P<col2>\d)(?P<layer2>\d)'
    clb_pattern=['[Yy](?P<clb_no>\d)(?P<y_no>\d)\s*', #LHS
        '(?P<ff_edge>!?)(?P<async_sync><?)(?P<clk_var>\w*)=' #sync or async
        ] 
    clb_pattern=''.join(clb_pattern)
    
    for code in codes:
        io_conn_box_result=re.search(io_conn_box_pattern,code)
        clb_conn_box_result=re.search(clb_conn_box_pattern,code)
        switch_box_result=re.search(switch_box_pattern,code)
        
        if io_conn_box_result:
            io_conn_box_bitstream(io_conn_box_result,cbox_data)
        elif clb_conn_box_result:
            clb_conn_box_bitstream(clb_conn_box_result,cbox_data)
        elif switch_box_result:
            switch_box_bitstream(switch_box_result,sbox_data)
    for expr in exprs:
        clb_result=re.search(clb_pattern,expr)
        clb_no=int(clb_result.group('clb_no'))
        clb_list[clb_no].clb_bitstream_gen(expr,mode,clb_result)

def get_exprs(code_lines:list)->list:
    """
    Used in mode 2 operation. Extracts the expressions from the codelines.

    Args:
        code_lines (list): Generalised code.

    Returns:
        expr (list): The expressions in the codelines.
    """
    exprs=[]
    for code in code_lines:
        expr_pattern='\w+ *!?<?= *'
        expr_result=re.search(expr_pattern,code)
        if expr_result:
            exprs.append(code)
    
    return exprs