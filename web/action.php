<?php

$process = new stdClass();
$process->furnance_id = 101;
$process->start_time = time();
$process->steps = Array();

for ($i = 1; $i <= 8; $i++) {
    if ($_POST["step$i-start-temperature"] != NULL && $_POST["step$i-end-temperature"] != NULL && $_POST["step$i-duration"]) {
        $step = new stdClass();
        $step->step_number = $i;
        $step->start_temperature = (int)$_POST["step$i-start-temperature"];
        $step->end_temperature = (int)$_POST["step$i-end-temperature"];
        $step->duration = (int)$_POST["step$i-duration"] * 60;
        array_push($process->steps, $step);
    }
}






$process = json_encode($process, JSON_PRETTY_PRINT);
 

$fp = fopen("../bakings/furnance-101.json", 'w');
fwrite($fp, $process);
fclose($fp);

echo "<pre>" . $process . "<pre/>";
