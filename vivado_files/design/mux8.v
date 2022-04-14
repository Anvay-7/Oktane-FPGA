module mux8 (
	input      [2:0] sel ,
	input      [7:0] data,
	output reg       y
);

	always@(*)
		begin
			case (sel)
				3'd0    : y<=data[0];
				3'd1    : y<=data[1];
				3'd2    : y<=data[2];
				3'd3    : y<=data[3];
				3'd4    : y<=data[4];
				3'd5    : y<=data[5];
				3'd6    : y<=data[6];
				3'd7    : y<=data[7];
				default : y<= 0;
			endcase
		end
endmodule
