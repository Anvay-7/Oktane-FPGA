module switch_box (
	inout       l, u, r, d,
	input [5:0] dir,
	input [5:0] en
);

	bidir_buf bdf1 (.left(l), .right(u), .dir(dir[0]), .en(en[0]));
	bidir_buf bdf2 (.left(u), .right(r), .dir(dir[1]), .en(en[1]));
	bidir_buf bdf3 (.left(r), .right(d), .dir(dir[2]), .en(en[2]));
	bidir_buf bdf4 (.left(d), .right(l), .dir(dir[3]), .en(en[3]));
	bidir_buf bdf5 (.left(l), .right(r), .dir(dir[4]), .en(en[4]));
	bidir_buf bdf6 (.left(u), .right(d), .dir(dir[5]), .en(en[5]));

endmodule
