module clb (
	input        si     ,
	input        sys_clk,
	input  [3:0] a, b, c,
	input  [2:0] clk    ,
	input        f_clk  ,
	output       so     ,
	output       y1, y2
);

	wire [32:0] cfg;

	shift_reg #(.len(33)) sr0 (.sin(si), .clk(sys_clk), .Q(cfg));
	assign so = cfg[32];

	wire clk_mux_y;
	mux4 clk_sel (.sel(cfg[1:0]), .data({f_clk,clk}), .y(clk_mux_y)); 

	wire c_mux_y;
	mux4 c_sel (.sel(cfg[3:2]), .data(c), .y(c_mux_y));

	wire b_mux_y;
	mux4 b_sel (.sel(cfg[5:4]), .data(b), .y(b_mux_y)); 

	wire a_mux_y;
	mux4 a_sel (.sel(cfg[7:6]), .data(a), .y(a_mux_y));

	assign a_val = cfg[14]?a_mux_y:0;
	assign b_val = cfg[15]?b_mux_y:0;
	assign c_val = cfg[16]?c_mux_y:0;

	mux8 lut1 (.sel({a_val,b_val,c_val}), .data(cfg[24:17]), .y(lut1_y));
	mux8 lut2 (.sel({a_val,b_val,c_val}), .data(cfg[32:25]), .y(lut2_y));

	assign y1_edge = cfg[12]?!clk_mux_y:clk_mux_y;
	assign y2_edge = cfg[13]?!clk_mux_y:clk_mux_y;

	reg y1_ff;
	always@(posedge y1_edge)
		begin
			y1_ff <= lut1_y;
		end

	reg y2_ff;
	always@(posedge y2_edge)
		begin
			y2_ff <= lut2_y;
		end

	assign y1_sync_async = cfg[8]?y1_ff:lut1_y;
	assign y2_sync_async = cfg[9]?y2_ff:lut2_y;

	assign y1 = cfg[10]?y1_sync_async:1'bz;
	assign y2 = cfg[11]?y2_sync_async:1'bz;

endmodule
