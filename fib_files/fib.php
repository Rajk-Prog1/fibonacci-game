<?php
function fib($n) {
    if ($n <= 2) {
        return 1;
    } else {
        return fib($n - 1) + fib($n - 2);
    }
}

$n_env = getenv("FIB_N");
$n = $n_env ? intval($n_env) : 40;

$sequence = [];
$start = microtime(true);

for ($i = 1; $i <= $n; $i++) {
    $val = fib($i);
    $sequence[] = $val;
    echo $i . ". fibonacci: " . $val . "\n";
}

$elapsed = microtime(true) - $start;

$result = [
    "language" => "PHP",
    "n" => $n,
    "sequence" => $sequence,
    "seconds" => $elapsed
];

file_put_contents("result_php.json", json_encode($result, JSON_PRETTY_PRINT));
?>


