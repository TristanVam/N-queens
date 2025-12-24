% Classic N-Queens using integer columns and alldifferent constraints
int: N;
array[1..N] of var 1..N: q;

constraint alldifferent(q);
constraint alldifferent([q[i] + i | i in 1..N]);
constraint alldifferent([q[i] - i | i in 1..N]);

solve satisfy;

output ["positions=[" ++ join(", ", ["(" ++ show(i) ++ "," ++ show(q[i]) ++ ")" | i in 1..N]) ++ "]\n"];
