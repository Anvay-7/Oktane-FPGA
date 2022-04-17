module test (
	input  wire a, b, sel,
	output wire q
);
	assign q = sel ? a : 1'bz;
	assign q = sel ? 1'bz : b;
endmodule