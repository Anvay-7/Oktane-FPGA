`timescale 1ns / 1ps
module test_tb ();

	reg     bitstream[272:0];
	integer i               ;

	initial
		begin
			#10 $readmemb("E:\\Oktane\\vivado_files\\bitstream.txt",bitstream);
            
			#10 flag =1;
            for (i=0;i<272;i=i+1)
            begin
                #10 sin = bitstream[i];
            end
            #10 flag = 0;

			$finish;
		end
endmodule
