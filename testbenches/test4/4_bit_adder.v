module adder_four_bit (input [3:0] A,
                   input [3:0] B,
                   //input clk,
                   input reset,
                   input start,
                   output done,
                   output [3:0] result);

   wire [3:0] result_add;

   bit clk;

   initial clk = 0;
   always #5 clk = ~clk;

   single_cycle adder (.A(A), .B(B), .clk(clk), .reset(reset), .start(start),
                       .done(done), .result(result_add));

   assign done = 1'b1;
   assign result = result_add;

endmodule // tiny_adder


module single_cycle(input [3:0] A,
                    input [3:0] B,
                    input clk,
                    input reset,
                    input start,
                    output logic done,
                    output logic [3:0] result);

  always @(posedge clk)
    if (!reset)
      result <= 4'b0;
    else
      result <= A + B;

   always @(posedge clk)
     if (!reset)
       done <= 0;
     else
       done <= start;

endmodule : single_cycle