`timescale 1ns / 1ps

module fpga_tb ();
	reg  [23:0] p     = 24'dz;
	reg         sin   = 0    ;
	reg         s_clk        ;
	reg         f_clk = 0    ;
	reg         flag         ;
	wire        sout         ;

	wire [23:0] pw;
	assign pw = p;

	reg     bitstream[1400:0];
	integer i                ;

	fpga f1 (.p(pw), .sin(sin), .s_clk(s_clk), .f_clk(f_clk), .flag(flag), .sout(sout));

	initial
		begin
			s_clk <= 0;
			forever #5 s_clk <= !s_clk;
		end

	initial
		begin
			flag =1;
			$readmemb("E:\\Oktane\\vivado_files\\bitstream.txt",bitstream);

			for (i=0;i<1401;i=i+1)
				begin
					#10 sin = bitstream[i];
				end

			#10 flag=0;

			#10 f_clk=0;
			#10 f_clk=1;

			#10 f_clk=0;
			#10 f_clk=1;

			#10 f_clk=0;
			#10 f_clk=1;

			#10 f_clk=0;
			#10 f_clk=1;

			#10 f_clk=0;
			#10 f_clk=1;

			#10 f_clk=0;
			#10 f_clk=1;

			#10 f_clk=0;
			#10 f_clk=1;

			#10 f_clk=0;
			#10 f_clk=1;

			// #10 p[0]=0;p[1]=0;
			// #10 p[0]=0;p[1]=1;
			// #10 p[0]=1;p[1]=0;
			// #10 p[0]=1;p[1]=1;
			#50 $finish;
		end


endmodule
