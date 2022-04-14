`timescale 1ns / 1ps

module clb_tb ();
	reg [32:0] cfg  ;
	reg [ 3:0] a    ;
	reg [ 3:0] b    ;
	reg [ 3:0] c    ;
	reg [ 2:0] clk  ;
	reg        f_clk;

	wire y1;
	wire y2;

	clb slice0 (.cfg(cfg), .a(a), .b(b), .c(c), .clk(clk), .f_clk(f_clk), .y1(y1), .y2(y2));

	initial
		begin
			f_clk <= 0;
			forever #5 f_clk <= !f_clk;
		end

	initial
		begin
			cfg <= 33'h12c01c8d3;
			a <= 4'b1010;
			b <= 4'b1010;
			c <= 4'b0z01;
			clk <= 3'b000;
			#12 a <= 4'b1100;
			#30 $finish;
		end
endmodule
