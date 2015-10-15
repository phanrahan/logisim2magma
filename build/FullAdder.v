module main (input [0:2] SWITCH, output [0:1] LED);
wire inst0_O;
wire inst1_O;
wire inst2_O;
wire inst3_O;
wire inst4_O;
LUT2 #(.INIT(4'h6)) inst0 (.I0(SWITCH[2]), .I1(SWITCH[1]), .O(inst0_O));
LUT2 #(.INIT(4'h8)) inst1 (.I0(SWITCH[1]), .I1(SWITCH[2]), .O(inst1_O));
LUT2 #(.INIT(4'hE)) inst2 (.I0(inst3_O), .I1(inst1_O), .O(inst2_O));
LUT2 #(.INIT(4'h8)) inst3 (.I0(inst0_O), .I1(SWITCH[0]), .O(inst3_O));
LUT2 #(.INIT(4'h6)) inst4 (.I0(inst0_O), .I1(SWITCH[0]), .O(inst4_O));
assign LED = {inst2_O, inst4_O};
endmodule

