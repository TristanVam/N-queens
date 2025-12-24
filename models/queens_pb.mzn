% Boolean pseudo-Boolean encoding of N-Queens
int: N;
array[1..N, 1..N] of var bool: x;

% Exactly one queen per row
constraint forall(r in 1..N) (
    sum([bool2int(x[r, c]) | c in 1..N]) = 1
);

% At most one queen per column
constraint forall(c in 1..N) (
    sum([bool2int(x[r, c]) | r in 1..N]) <= 1
);

% At most one queen per \ diagonal (r - c constant)
set of int: DIFFS = {-N + 1..N - 1};
constraint forall(d in DIFFS) (
    sum([bool2int(x[r, c]) | r in 1..N, c in 1..N where r - c = d]) <= 1
);

% At most one queen per / diagonal (r + c constant)
set of int: SUMS = {2..2 * N};
constraint forall(s in SUMS) (
    sum([bool2int(x[r, c]) | r in 1..N, c in 1..N where r + c = s]) <= 1
);

solve satisfy;

output [
  "positions=[" ++
  join(", ", ["(" ++ show(r) ++ "," ++ show(c) ++ ")" | r in 1..N, c in 1..N where fix(x[r, c])]) ++
  "]\n"
];
