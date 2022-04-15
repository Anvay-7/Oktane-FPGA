`timescale 1ns / 1ps

module conn_box_tb ();
	reg  [3:0] a  ;
	reg        b  ;
	reg        clk;
	reg        si ;
	wire       so ;

	wire [3:0] aw;
	assign aw = a;
	assign bw = b;

	conn_box c0 (.a(aw), .b(bw), .clk(clk), .si(si), .so(so));

	initial
		begin
			clk <= 0;
			forever #5 clk <= !clk;
		end

	initial
		begin
			a = 4'bz0z1;
			b = 1'bz;

			si = 1;
			#10 si = 0;
			#10 si = 1;
			#10 si = 1;
			#10 si = 1;
			#10 si = 0;
			#10 si = 0;
			#10 si = 0;
			#20 $finish;
		end

endmodule
