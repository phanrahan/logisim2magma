module main (input [0:1] SWITCH, output [0:1] LED);
wire inst0_O;
wire inst1_O;
LUT2 #(.INIT(4'h1)) inst0 (.I0(inst1_O), .I1(SWITCH[1]), .O(inst0_O));
LUT2 #(.INIT(4'h1)) inst1 (.I0(SWITCH[0]), .I1(inst0_O), .O(inst1_O));
assign LED = {inst1_O, inst0_O};
endmodule

