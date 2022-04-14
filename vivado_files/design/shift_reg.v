module shift_reg #(parameter len=4) (
	input            sin,
	input            clk,
	output reg [len-1:0] Q
);

	always@(posedge clk)
		begin
			Q <= {Q[len-2:0],sin};
		end
endmodule
