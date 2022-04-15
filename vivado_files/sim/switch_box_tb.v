`timescale 1ns / 1ps

module switch_box_tb ();
	reg  a  ;
	reg  b  ;
	reg  c  ;
	reg  d  ;
	reg  clk;
	reg  si ;
	wire so ;

	assign aw = a;
	assign bw = b;
	assign cw = c;
	assign dw = d;
	
	switch_box s0 (.l(aw), .u(bw), .r(cw), .d(dw), .clk(clk), .si(si), .so(so));

	initial
		begin
			clk <= 0;
			forever #5 clk <= !clk;
		end

	initial
		begin
			a = 1'b1;
			b = 1'bz;
			c = 1'bz;
			d = 1'bz;

			si = 1;
			#10 si = 0;
			#10 si = 1;
			#10 si = 1;
			#10 si = 1;
			#10 si = 1;
			#10 si = 0;
			#10 si = 0;
			#10 si = 0;
			#10 si = 0;
			#10 si = 1;
			#10 si = 1;
			#20 $finish;
		end

endmodule
