`timescale 1ns / 1ps

module mux4_tb ();

	reg  [1:0] sel           ;
	reg  [3:0] data = 4'b1101;
	wire       y             ;

	mux4 m1 (.sel(sel), .data(data), .y(y));

	initial
		begin
			sel =  2'b00;
			#5 sel =  2'b01;
			#5 sel =  2'b10;
			#5 sel =  2'b11;
			#5 $finish;
		end

endmodule
