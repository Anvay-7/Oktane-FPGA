import imp
import random
import code_read as cdr
import graph_nw as gnw
import placement as pl
import bit_stream_funcs as bsf
import config as cfg
import colorama
from gui import exec_prgs

def main(exec_progress:exec_prgs,AHDL7_file_dir:str)->None:
    """
    All the placement, routing and bitstream generation modules are integrated here.

    Args:
        exec_progress (exec_prg): The code execution progress window object
        AHDL7_file_dir (str): Path to the AHDL7 code
    """
    cdr.status_field_write(exec_progress,"Starting :)")
    cdr.update_prog_bar(exec_progress,1)
    
    # Uncomment the line below if you want to get same results everytime.
    random.seed(21)

    colorama.init()  # To make color text work on windows terminal

    clbs = []
    clbs_data = []

    # Instantiating all the CLB's
    for clb_no in range(cfg.CLB_CNT):
        clbs.append(bsf.Clb(clb_no))
        clbs_data.append(clbs[clb_no].data)
    
    code_lines = cdr.AHDL7_read(AHDL7_file_dir)

    mode = cdr.get_mode(code_lines[0])  # Automatic or manual

    code_lines.pop(0)  # Remove the mode assignment

    # Instantiate all the ROM's
    rom = cdr.WriteMem(r"D:\Oktane\Oktane_simulator_files")
    rom.make_dir()

    routing_nw = gnw.route_nw_gen()
    clb_nw = pl.clb_nw_gen()

    # default bitstream for switch boxes
    sbox_data = {}
    for i in range(rom.sw_box_count*2): #Two groups of sw_box(8 sw_boxes totally) data in one ROM
        for j in range(cfg.ROUTE_CHNL_SIZE):
            sbox_data[f"s{i}{j}"] = "000000"

    # default bitstream for connection boxes
    cbox_data = {}
    for i in range(rom.conn_box_count):
        cbox_data[f"c{i}"] = "0000"
    
    cdr.status_field_write(exec_progress,"Initialisation done")
    cdr.update_prog_bar(exec_progress,2)
    
    
    if mode == 1:
        final_codelines, paths, conv_exprs = pl.placer(routing_nw, clb_nw, code_lines)
        print(final_codelines)
        print(conv_exprs)
        
        codes = gnw.detailed_code_gen(paths, clbs)

        bsf.bit_stream_config_gen(codes, conv_exprs, mode, clbs, cbox_data, sbox_data)
        
        cdr.status_field_write(exec_progress,"Bitstream generated")
        cdr.update_prog_bar(exec_progress,4)
        
    elif mode == 2:
        cost_path=gnw.get_paths_cost(routing_nw,code_lines)
        paths = cost_path[1]
        codes = gnw.detailed_code_gen(paths, clbs)
        exprs = bsf.get_exprs(code_lines)
        bsf.bit_stream_config_gen(codes, exprs, mode, clbs, cbox_data, sbox_data)
        
        cdr.status_field_write(exec_progress,"Bitstream generated")
        cdr.update_prog_bar(exec_progress,4)
        
    rom.switch_box(sbox_data)
    rom.conn_box(cbox_data)
    rom.clb(clbs)
    
    cdr.status_field_write(exec_progress,"Bitstream written to ROM")
    cdr.update_prog_bar(exec_progress,5)
    
    cdr.status_field_write(exec_progress,"Completed")
    
    for i in range(9):
        print("{0:09x}".format(int(clbs[i].data, 2)))
        
        
if __name__== "__main__":
    main()
