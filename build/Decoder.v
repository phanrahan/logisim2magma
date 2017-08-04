module main (input [0:1] SWITCH, output [0:3] LED);
wire inst0_O;
wire inst1_O;
wire inst2_O;
wire inst3_O;
wire inst4_O;
wire inst5_O;
LUT1 #(.INIT(2'h1)) inst0 (.I0(SWITCH[0]), .O(inst0_O));
LUT2 #(.INIT(4'h8)) inst1 (.I0(SWITCH[0]), .I1(SWITCH[1]), .O(inst1_O));
LUT2 #(.INIT(4'h8)) inst2 (.I0(SWITCH[0]), .I1(inst5_O), .O(inst2_O));
LUT2 #(.INIT(4'h8)) inst3 (.I0(inst0_O), .I1(inst5_O), .O(inst3_O));
LUT2 #(.INIT(4'h8)) inst4 (.I0(inst0_O), .I1(SWITCH[1]), .O(inst4_O));
LUT1 #(.INIT(2'h1)) inst5 (.I0(SWITCH[1]), .O(inst5_O));
assign LED = {inst3_O, inst2_O, inst4_O, inst1_O};
endmodule

