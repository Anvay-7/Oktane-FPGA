import os
import xml.etree.ElementTree as ET
import re
import config as cfg

def AHDL7_read(directory: str) -> list:
    """
    Reads the contents of the AHDL7 code file, line by line. Also ignores the comments.

    Args:
        directory (str): Path to code file

    Returns:
        lines (list): All the code lines
    """
    with open(directory) as file:
        lines = []
        while True:
            line = file.readline()
            if not line:
                break

            # Remove the comments
            comm_pos = line.find("#")
            if comm_pos != -1:
                line = line[0:comm_pos].strip()

            # Remove the \n escape character
            if line.rstrip():
                lines.append(line.rstrip())

    return lines


def get_mode(code: str) -> int:
    """
    Extracts the mode number.

    Args:
        code (str): code containing mode number

    Returns:
        int: Mode number
    """

    mode_pattern = "mode *: *(?P<mode>\d)"
    mode_result = re.search(mode_pattern, code, re.IGNORECASE)
    mode = int(mode_result.group("mode"))

    return mode


def link_ROM(directory:str, name:str, path:str):
    """
    Links config file to the simulator ROM. 

    Args:
        directory (str): The path to FPGA Slice folder
        name (str): The name of the element
        path (str): The path to the element's hex file
    """
    mytree = ET.parse(os.path.join(directory, "fpga_ckt.dig"))
    root = mytree.getroot()

    elements_branch = root.findall("visualElements/visualElement")
    for element in elements_branch:
        flag = False
        if element.find("elementName").text == "ROM":
            entry_branch = element.findall("elementAttributes/entry")
            for entry in entry_branch:
                string_branch = entry.findall("string")
                for strng in string_branch:
                    if strng.text == name:
                        flag = True
                if flag:
                    if entry.find("file") == None:
                        pass
                    else:
                        entry.find("file").text = path

    mytree.write(os.path.join(directory, "fpga_ckt.dig"))


class WriteMem:
    """
    Contains all the methods required to write data to ROM.
    """

    def __init__(self, directory: str)->None:
        """
        Args:
            directory (str): Path where the ROM folders are. 
        """
        self.dir = directory
        self.sw_box_count = ((cfg.ROWS_CNT+1)*(cfg.COLS_CNT+1))//2 #Divide by 2 as two groups of sw_box's in one ROM
        
        self.conn_box_count=(cfg.ROWS_CNT+cfg.COLS_CNT)*cfg.IO_GRP_SIZE*2+(cfg.CLB_CNT*2)
                
    def serial_bitstream(self,sbox_data,conn_box_config,clb_list):
        order=[
            's0','c23','c22','s1','c21','c20','s2','c19','c18','s3',
            'c28','c17','c16','c29','d2','c26','c27','d1','c24','c25','d0','c0','c1',
            's4','s5','s6','s7',
            'c34','c15','c14','c35','d5','c32','c33','d4','c30','c31','d3','c2','c3','s8',
            's9','s10','s11','c40',
            'c13','c12','c41','d8','c38','c39','d7','c36','c37','d6','c4','c5','s12',
            'c6','c7','s13','c8','c9','s14','c10','c11','s15'     
               ]
        order.reverse()

        cfg_data=[]
        switch_pattern="[Ss](?P<sbox_no>\d{1,2})"
        conn_box_pattern = "[Cc](?P<cbox_no>\d{1,2})"
        clb_pattern="[Dd](?P<clb_no>\d)"
        print(sbox_data)
        for block in order:
            switch_res=re.search(switch_pattern,block)
            if switch_res:
                for i in range(4):
                    cfg_data.append((sbox_data[f"s{switch_res.group('sbox_no')}{3-i}"])[::-1])
            
            conn_box_res=re.search(conn_box_pattern,block)
            if conn_box_res:
                cfg_data.append((conn_box_config[f"c{conn_box_res.group('cbox_no')}"])[::-1])
            
            clb_res=re.search(clb_pattern,block)
            if clb_res:
                cfg_data.append('000'+(clb_list[int(clb_res.group('clb_no'))].data))
                   
        bitstream=''.join(cfg_data) 
        bitstream=list(bitstream)
        bitstream_file=r"Oktane_simulator_files\config_data\bitstream.hex"
        with open(bitstream_file,'w') as file:
            file.write("v2.0 raw\n0")
            for i in bitstream:
                file.write('\n'+i)
        
        link_ROM(self.dir,"bitstream", os.path.join(self.dir,bitstream_file))

def status_field_write(ide,msg):
    ide.w.txt.csr.insertText(f"{msg}\n")
    ide.w.txt.moveCursor(ide.w.txt.csr.End)
    
def update_prog_bar(ide,progress):
    ide.w.pg_bar.pg_bar_value.emit(progress)
    