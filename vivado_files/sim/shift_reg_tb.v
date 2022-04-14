`timescale 1ns / 1ps

module shift_reg_tb #(parameter len = 5) ();
	reg            sin       ;
	reg            clk = 1'b0;
	wire [len-1:0] Q         ;

	shift_reg #(.len(len)) sr (.sin(sin), .clk(clk), .Q(Q));

	initial
		begin
			forever #5 clk<= !clk;
		end

	initial
		begin
			sin <= 1;
			#10 sin <= 0;
			#10 sin <= 1;
			#10 sin <= 0;
			#100 $finish;
		end

endmodule
