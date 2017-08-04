module main (input [0:1] SWITCH, output [0:7] LED);
wire inst0_O;
wire inst1_O;
wire inst2_O;
wire inst3_O;
wire inst4_O;
wire inst5_O;
wire inst6_O;
wire inst7_O;
LUT2 #(.INIT(4'h9)) inst0 (.I0(SWITCH[0]), .I1(SWITCH[1]), .O(inst0_O));
LUT2 #(.INIT(4'h8)) inst1 (.I0(SWITCH[0]), .I1(SWITCH[1]), .O(inst1_O));
LUT2 #(.INIT(4'hE)) inst2 (.I0(SWITCH[0]), .I1(SWITCH[1]), .O(inst2_O));
LUT2 #(.INIT(4'h7)) inst3 (.I0(SWITCH[0]), .I1(SWITCH[1]), .O(inst3_O));
LUT1 #(.INIT(2'h2)) inst4 (.I0(SWITCH[1]), .O(inst4_O));
LUT2 #(.INIT(4'h1)) inst5 (.I0(SWITCH[0]), .I1(SWITCH[1]), .O(inst5_O));
LUT2 #(.INIT(4'h6)) inst6 (.I0(SWITCH[0]), .I1(SWITCH[1]), .O(inst6_O));
LUT1 #(.INIT(2'h2)) inst7 (.I0(SWITCH[0]), .O(inst7_O));
assign LED = {inst7_O, inst4_O, inst1_O, inst3_O, inst2_O, inst5_O, inst6_O, inst0_O};
endmodule

