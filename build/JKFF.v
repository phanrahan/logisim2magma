module main (input [0:2] SWITCH, output [0:1] LED);
wire inst0_O;
wire inst1_O;
wire inst2_O;
wire inst3_O;
wire inst4_O;
wire inst5_O;
wire inst6_O;
wire inst7_O;
wire inst8_O;
wire inst9_O;
wire inst10_O;
LUT3 #(.INIT(16'h8080)) inst0 (.I0(inst6_O), .I1(SWITCH[1]), .I2(inst8_O), .O(inst0_O));
LUT2 #(.INIT(4'h1)) inst1 (.I0(inst5_O), .I1(inst3_O), .O(inst1_O));
LUT3 #(.INIT(16'h8080)) inst2 (.I0(SWITCH[2]), .I1(inst8_O), .I2(inst9_O), .O(inst2_O));
LUT2 #(.INIT(4'h1)) inst3 (.I0(inst1_O), .I1(inst10_O), .O(inst3_O));
LUT2 #(.INIT(4'h1)) inst4 (.I0(inst0_O), .I1(inst7_O), .O(inst4_O));
LUT2 #(.INIT(4'h8)) inst5 (.I0(SWITCH[0]), .I1(inst4_O), .O(inst5_O));
LUT2 #(.INIT(4'h7)) inst6 (.I0(inst1_O), .I1(SWITCH[2]), .O(inst6_O));
LUT2 #(.INIT(4'h1)) inst7 (.I0(inst4_O), .I1(inst2_O), .O(inst7_O));
LUT1 #(.INIT(2'h1)) inst8 (.I0(SWITCH[0]), .O(inst8_O));
LUT2 #(.INIT(4'h7)) inst9 (.I0(SWITCH[1]), .I1(inst3_O), .O(inst9_O));
LUT2 #(.INIT(4'h8)) inst10 (.I0(inst7_O), .I1(SWITCH[0]), .O(inst10_O));
assign LED = {inst1_O, inst3_O};
endmodule

