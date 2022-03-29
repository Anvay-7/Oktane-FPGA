import os
from tkinter.messagebox import NO
import xml.etree.ElementTree as ET
import re
import config as cfg
import math
import bit_stream_funcs as bsf

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
        self.sw_box_cfg = ["" for _ in range(self.sw_box_count)]
        
        self.conn_box_count=(cfg.ROWS_CNT+cfg.COLS_CNT)*cfg.IO_GRP_SIZE*2+(cfg.CLB_CNT*2)
        self.conn_box_cfg = ["" for _ in range(math.ceil(self.conn_box_count/16))]
        
        self.clb_data_cfg = ["" for _ in range(cfg.CLB_CNT)]

    def make_dir(self)->None:
        """
        Creates the folders(if not created already) required to store the data.
        """        
        # Create all the necessary folders
        if not os.path.isdir(os.path.join(self.dir, "config_data")):
            os.mkdir(os.path.join(self.dir, "config_data"))

        self.sw_cfg_data_folder_path = os.path.join(
            self.dir, "config_data", "sw_cfg_data"
        )
        if not os.path.isdir(self.sw_cfg_data_folder_path):
            os.mkdir(self.sw_cfg_data_folder_path)

        self.conn_box_cfg_data_folder_path = os.path.join(
            self.dir, "config_data", "conn_box_cfg_data"
        )
        if not os.path.isdir(self.conn_box_cfg_data_folder_path):
            os.mkdir(self.conn_box_cfg_data_folder_path)

        self.io_cfg_data_folder_path = os.path.join(
            self.dir, "config_data", "io_cfg_data"
        )
        if not os.path.isdir(self.io_cfg_data_folder_path):
            os.mkdir(self.io_cfg_data_folder_path)

        self.clb_cfg_data_folder_path = os.path.join(
            self.dir, "config_data", "clb_cfg_data"
        )
        if not os.path.isdir(self.clb_cfg_data_folder_path):
            os.mkdir(self.clb_cfg_data_folder_path)

    def switch_box(self, sbox_data:dict)->None:
        """
        Divide the switch box bitstreams into different ROM's
        write bitstream for 8 switch boxes(2 groups) into a single ROM

        Args:
            sbox_data (dict): Bitstream for switch boxes. eg {'s0':'010010'}
        """
        rom_no = -1
        for i in range(self.sw_box_count*2):
            if i % 2 == 0:
                rom_no += 1
            for j in range(cfg.ROUTE_CHNL_SIZE):
                self.sw_box_cfg[rom_no] = (
                    self.sw_box_cfg[rom_no] + sbox_data["s" + str(i) + str(j)]
                )

        # Write the switch box bitstream to ROM
        #Each ROM can hold 48 bits or 8 switch box's data
        for i in range(self.sw_box_count):
            self.sw_box_cfg[i] = "{:012x}".format(int(self.sw_box_cfg[i][::-1], 2))
            final_code_str = "v2.0 raw\n" + self.sw_box_cfg[i]
    
            file = open(
                os.path.join(
                    self.sw_cfg_data_folder_path, "sw_data_cfg_" + str(i) + ".hex"
                ),
                "w+",
            )
            link_ROM(
                self.dir,
                "sw-cfg" + str(i),
                os.path.join(
                    self.sw_cfg_data_folder_path, "sw_data_cfg_" + str(i) + ".hex"
                ),
            )
            file.write(final_code_str)
            file.close()

    def conn_box(self, conn_box_config:dict,)->None:
        """
        Divide the connection box bitstreams into different ROM's
        write bitstream for 16 connection boxes into a single ROM

        Args:
            conn_box_config (dict): Bitstream for connection boxes. eg {'c0':'0100'}
        """
        rom_no=-1
        for i in range(self.conn_box_count):
            
            #Each ROM can hold 64 bits or 16 connection box's data    
            if (i%16)==0:
                rom_no+=1
            
            self.conn_box_cfg[rom_no] = (
                self.conn_box_cfg[rom_no] + conn_box_config["c" + str(i)]
            )

        # write the connection box bitstream to the ROM
        for i in range(math.ceil(self.conn_box_count/16)):
            self.conn_box_cfg[i] = "{:012x}".format(int(self.conn_box_cfg[i][::-1], 2))
            final_code_str = "v2.0 raw\n" + self.conn_box_cfg[i]
            # file= open("D:\Documents\digital projects\FPGA slice\conn_box_cfg_"+str(i+1)+".hex","w+")
            file = open(
                os.path.join(
                    self.conn_box_cfg_data_folder_path,
                    "conn_box_data_cfg_" + str(i) + ".hex",
                ),
                "w+",
            )
            link_ROM(
                self.dir,
                "conn-cfg" + str(i),
                os.path.join(
                    self.conn_box_cfg_data_folder_path,
                    "conn_box_data_cfg_" + str(i) + ".hex",
                ),
            )
            file.write(final_code_str)
            file.close()

    def clb(self, clb_list:list[bsf.Clb])->None:
        """
        Write the CLB bitstream into respective ROM's

        Args:
            clb_list (list[bsf.Clb]): All the instantiated Clb objects
        """
        for i in range(9):
            self.clb_data_cfg[i] = "{0:09x}".format(int(clb_list[i].data, 2))
            final_code_str = "v2.0 raw\n" + self.clb_data_cfg[i]
            file = open(
                os.path.join(
                    self.clb_cfg_data_folder_path, "clb_data_cfg_" + str(i) + ".hex"
                ),
                "w+",
            )
            link_ROM(
                self.dir,
                "slice-cfg" + str(i),
                os.path.join(
                    self.clb_cfg_data_folder_path, "clb_data_cfg_" + str(i) + ".hex"
                ),
            )
            file.write(final_code_str)
            file.close()

def status_field_write(ide,msg):
    ide.w.txt.csr.insertText(f"{msg}\n")
    ide.w.txt.moveCursor(ide.w.txt.csr.End)
    
def update_prog_bar(ide,progress):
    ide.w.pg_bar.pg_bar_value.emit(progress)
    