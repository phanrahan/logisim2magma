module main (input [0:1] SWITCH, output [0:0] LED);
wire inst0_O;
wire inst1_O;
wire inst2_O;
wire inst3_O;
LUT2 #(.INIT(4'h7)) inst0 (.I0(SWITCH[0]), .I1(SWITCH[1]), .O(inst0_O));
LUT2 #(.INIT(4'h7)) inst1 (.I0(inst0_O), .I1(SWITCH[1]), .O(inst1_O));
LUT2 #(.INIT(4'h7)) inst2 (.I0(SWITCH[0]), .I1(inst0_O), .O(inst2_O));
LUT2 #(.INIT(4'h7)) inst3 (.I0(inst2_O), .I1(inst1_O), .O(inst3_O));
assign LED = {inst3_O};
endmodule

