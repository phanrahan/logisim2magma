module main (input [0:0] SWITCH, output [0:7] LED);
wire inst0_Q;
wire inst1_O;
wire inst2_Q;
wire inst3_O;
wire inst4_Q;
wire inst5_O;
wire inst6_Q;
wire inst7_O;
FDRSE #(.INIT(1'b0)) inst0 (.CE(1'b1), .R(1'b0), .S(1'b0), .D(inst1_O), .Q(inst0_Q));
LUT3 #(.INIT(16'h4E4E)) inst1 (.I0(inst0_Q), .I1(1'b1), .I2(1'b1), .O(inst1_O));
FDRSE #(.INIT(1'b0)) inst2 (.CE(1'b1), .R(1'b0), .S(1'b0), .D(inst3_O), .Q(inst2_Q));
LUT3 #(.INIT(16'h4E4E)) inst3 (.I0(inst2_Q), .I1(1'b1), .I2(1'b1), .O(inst3_O));
FDRSE #(.INIT(1'b0)) inst4 (.CE(1'b1), .R(1'b0), .S(1'b0), .D(inst5_O), .Q(inst4_Q));
LUT3 #(.INIT(16'h4E4E)) inst5 (.I0(inst4_Q), .I1(1'b1), .I2(1'b1), .O(inst5_O));
FDRSE #(.INIT(1'b0)) inst6 (.CE(1'b1), .R(1'b0), .S(1'b0), .D(inst7_O), .Q(inst6_Q));
LUT3 #(.INIT(16'h4E4E)) inst7 (.I0(inst6_Q), .I1(1'b1), .I2(1'b1), .O(inst7_O));
endmodule

