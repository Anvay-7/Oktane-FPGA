module conn_box (
	inout [3:0] a  ,
	inout       b  ,
	input [3:0] dir,
	input [3:0] en
);

	bidir_buf bdf3 (.left(a[3]), .right(b), .dir(dir[3]), .en(en[3]));
	bidir_buf bdf2 (.left(a[2]), .right(b), .dir(dir[2]), .en(en[2]));
	bidir_buf bdf1 (.left(a[1]), .right(b), .dir(dir[1]), .en(en[1]));
	bidir_buf bdf0 (.left(a[0]), .right(b), .dir(dir[0]), .en(en[0]));

endmodule
