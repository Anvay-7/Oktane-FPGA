module switch_box (
	inout  l, u, r, d,
	input  clk,
	input  si ,
	output so
);

	wire [11:0] po;

	shift_reg #(.len(12)) sr0 (.sin(si), .clk(clk), .Q(po));
	assign so = po[11];

	wire [5:0] en ;
	wire [5:0] dir;
	assign en  = po[5:0];
	assign dir = po[11:6];

	bidir_buf bdf1 (.left(l), .right(u), .dir(dir[0]), .en(en[0]));
	bidir_buf bdf2 (.left(u), .right(r), .dir(dir[1]), .en(en[1]));
	bidir_buf bdf3 (.left(r), .right(d), .dir(dir[2]), .en(en[2]));
	bidir_buf bdf4 (.left(d), .right(l), .dir(dir[3]), .en(en[3]));
	bidir_buf bdf5 (.left(l), .right(r), .dir(dir[4]), .en(en[4]));
	bidir_buf bdf6 (.left(u), .right(d), .dir(dir[5]), .en(en[5]));

endmodule
