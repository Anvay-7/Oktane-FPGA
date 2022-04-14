`timescale 1ns / 1ps

module bidir_buf_tb ();

	reg l  ;
	reg r  ;
	reg dir;
	reg en ;

	assign lw = l;
	assign rw = r;
	bidir_buf b1 (lw,rw,dir,en);

	initial
		begin
			l = 0;
			r = 1'bz;
			dir = 0;
			en = 1;
			#20 $finish;
		end

endmodule
