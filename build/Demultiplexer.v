module main (input [0:2] SWITCH, output [0:3] LED);
wire inst0_O;
wire inst1_O;
wire inst2_O;
wire inst3_O;
wire inst4_O;
wire inst5_O;
LUT3 #(.INIT(16'h8080)) inst0 (.I0(inst3_O), .I1(SWITCH[0]), .I2(SWITCH[2]), .O(inst0_O));
LUT3 #(.INIT(16'h8080)) inst1 (.I0(SWITCH[1]), .I1(SWITCH[0]), .I2(inst4_O), .O(inst1_O));
LUT3 #(.INIT(16'h8080)) inst2 (.I0(inst3_O), .I1(SWITCH[0]), .I2(inst4_O), .O(inst2_O));
LUT1 #(.INIT(2'h1)) inst3 (.I0(SWITCH[1]), .O(inst3_O));
LUT1 #(.INIT(2'h1)) inst4 (.I0(SWITCH[2]), .O(inst4_O));
LUT3 #(.INIT(16'h8080)) inst5 (.I0(SWITCH[1]), .I1(SWITCH[0]), .I2(SWITCH[2]), .O(inst5_O));
assign LED = {inst2_O, inst1_O, inst0_O, inst5_O};
endmodule

