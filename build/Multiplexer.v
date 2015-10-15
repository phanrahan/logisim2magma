module main (input [0:5] SWITCH, output [0:0] LED);
wire inst0_O;
wire inst1_O;
wire inst2_O;
wire inst3_O;
wire inst4_O;
wire inst5_O;
wire inst6_O;
LUT1 #(.INIT(2'h1)) inst0 (.I0(SWITCH[4]), .O(inst0_O));
LUT3 #(.INIT(16'h8080)) inst1 (.I0(SWITCH[4]), .I1(SWITCH[3]), .I2(SWITCH[5]), .O(inst1_O));
LUT4 #(.INIT(16'hFFFE)) inst2 (.I0(inst4_O), .I1(inst3_O), .I2(inst5_O), .I3(inst1_O), .O(inst2_O));
LUT3 #(.INIT(16'h8080)) inst3 (.I0(SWITCH[4]), .I1(SWITCH[1]), .I2(inst6_O), .O(inst3_O));
LUT3 #(.INIT(16'h8080)) inst4 (.I0(inst0_O), .I1(SWITCH[0]), .I2(inst6_O), .O(inst4_O));
LUT3 #(.INIT(16'h8080)) inst5 (.I0(inst0_O), .I1(SWITCH[2]), .I2(SWITCH[5]), .O(inst5_O));
LUT1 #(.INIT(2'h1)) inst6 (.I0(SWITCH[5]), .O(inst6_O));
assign LED = {inst2_O};
endmodule

