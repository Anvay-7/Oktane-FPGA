`timescale 1ns / 1ps

module conn_box_tb ();
	reg [3:0] a  ;
	reg       b  ;
	reg [3:0] dir;
	reg [3:0] en ;

	wire [3:0] aw;
	assign aw = a;
	assign bw = b;

	conn_box c0 (.a(aw), .b(bw), .dir(dir), .en(en));

	initial
		begin
			a = 4'bz0z1;
			b = 1'bz;
			dir = 4'b1110;
			en = 4'b0011;
			#20 $finish;
		end

endmodule
