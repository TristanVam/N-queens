% Classic N-Queens using integer columns and alldifferent constraints
int: N;
bool: symmetry_break = false;
array[1..N] of var 1..N: q;

constraint alldifferent(q);
constraint alldifferent([q[i] + i | i in 1..N]);
constraint alldifferent([q[i] - i | i in 1..N]);

% Optional symmetry breaking: place the first queen in the left half
% to avoid mirrored solutions while keeping feasibility.
constraint if symmetry_break then q[1] <= (N + 1) div 2 else true endif;

solve satisfy;

output ["positions=[" ++ join(", ", ["(" ++ show(i) ++ "," ++ show(q[i]) ++ ")" | i in 1..N]) ++ "]\n"];
