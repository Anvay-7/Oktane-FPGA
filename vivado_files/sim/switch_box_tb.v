`timescale 1ns / 1ps

module switch_box_tb ();
	reg       a  ;
	reg       b  ;
	reg       c  ;
	reg       d  ;
	reg [5:0] dir;
	reg [5:0] en ;

	assign aw = a;
	assign bw = b;
	assign cw = c;
	assign dw = d;


	switch_box s0 (.l(aw), .u(bw), .r(cw), .d(dw), .dir(dir), .en(en));

	initial
		begin
			a = 1'b1;
			b = 1'bz;
			c = 1'bz;
			d = 1'bz;
			dir = 6'b000000;
			en = 6'b010000;
            #20 $finish;
		end

endmodule
