module main (input [0:2] SWITCH, output [0:1] LED);
wire inst0_O;
wire inst1_O;
wire inst2_O;
wire inst3_O;
LUT2 #(.INIT(4'h8)) inst0 (.I0(SWITCH[0]), .I1(SWITCH[2]), .O(inst0_O));
LUT2 #(.INIT(4'h8)) inst1 (.I0(SWITCH[1]), .I1(SWITCH[0]), .O(inst1_O));
LUT2 #(.INIT(4'h1)) inst2 (.I0(inst1_O), .I1(inst3_O), .O(inst2_O));
LUT2 #(.INIT(4'h1)) inst3 (.I0(inst2_O), .I1(inst0_O), .O(inst3_O));
assign LED = {inst2_O, inst3_O};
endmodule

