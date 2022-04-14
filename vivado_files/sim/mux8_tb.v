`timescale 1ns / 1ps

module mux8_tb ();

	reg  [2:0] sel               ;
	reg  [7:0] data = 8'b11100011;
	wire       y                 ;

	mux8 m1 (.sel(sel), .data(data), .y(y));

	initial
		begin
			sel =  3'd0;
			#5 sel =  3'd1;
			#5 sel =  3'd2;
			#5 sel =  3'd3;
			#5 sel =  3'd4;
			#5 sel =  3'd5;
			#5 sel =  3'd6;
			#5 sel =  3'd7;
			#5 $finish;
		end

endmodule
