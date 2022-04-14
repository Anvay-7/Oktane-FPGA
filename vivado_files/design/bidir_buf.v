module bidir_buf (
	inout left ,
	inout right,
	input dir  ,
	input en
);

	assign and1 = dir & en;
	assign and2 = ~dir & en;

	assign left  = and1?right:1'bz;
	assign right = and2?left:1'bz;

endmodule
