% Classic N-Queens using integer columns and alldifferent constraints
int: N;
bool: symmetry_break = false; % optional, off by default
array[1..N] of var 1..N: q;

constraint alldifferent(q);
constraint alldifferent([q[i] + i | i in 1..N]);
constraint alldifferent([q[i] - i | i in 1..N]);

% Optional symmetry breaking: restrict first row queen to first half of columns
constraint symmetry_break -> q[1] <= ceil(N / 2);

solve satisfy;

output ["positions=[" ++ join(", ", ["(" ++ show(i) ++ "," ++ show(q[i]) ++ ")" | i in 1..N]) ++ "]\n"];
