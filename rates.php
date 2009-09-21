<html>
<head>
<link rel="stylesheet" href="rates.css?<?php echo @filemtime('rates.css'); ?>">
<title>industrial bank &amp; agora</title>
</head>
<body>
<?php
if(@filemtime('.agd.cache') < max(@filemtime('agdump.py'), @filemtime('iba.txt'))) {
    passthru('python agdump.py 2>&1 > .agd.cache');
}
list($rates, $prev, $parties, $order, $contract, $holdings) = json_decode(file_get_contents('.agd.cache'));
$loser = $parties[0];
?>
<div id="links">
<a class="link linkactive" href="#calc" onclick="return go(0);">[rate calculator]</a>
<a class="link" href="#contract" onclick="return go(1);">contract</a>
<a class="link" href="#report" onclick="return go(2);">report</a>
</div>
<div id="sectionreport">
<?php
$iba = file_get_contents('iba.txt');
$iba = preg_replace('/^Date of this report: .*$/m', 'Last updated: (unknown)', $iba);
echo $iba;
?>
</div>
<div id="sectioncontract">
<?php echo $contract; ?>
</div>
<div id="sectionrate">
<table id="tab">
<tr>
<th>asset</th>
<th>rate (zm)</th>
<th># in bank</th>
<th style="background-color: #424242"></th>
<th>you</th>
<?php
$data = array();
$rated = false;
foreach($rates as $rate) {
    if(gettype($rate) == 'string') {
        if(substr($rate, 0, 3) == '-- ') {
            echo "<tr><td class='ghost' colspan='5'" . ($rated ? "" : " id='aaa'") . "><b>" . htmlentities(substr($rate, 3)) . "</b>";
            $rated = true;
        }
    } else {
        if($rate[0] == 'Drop your Wea..') $rate[0] = 'Drop your Weapon';
        $data[$rate[0]] = array($rate[0], $rate[1], $rate[2], 0);
        $banks = $rate[2] == 0 ? '' : $rate[2];
        echo "<tr id='tr-{$rate[0]}'><td>{$rate[0]}</td><td class='rate'>{$rate[1]}</td><td class='rate' id='banks-{$rate[0]}'>{$banks}</td><td class='btab'><button onclick=\"return c(-1,'{$rate[0]}');\">&laquo;</button><button id='ra-{$rate[0]}' onclick=\"return c(1,'{$rate[0]}');\">&raquo;</button></td><td class='mine' id='mine-{$rate[0]}'></td></tr>\n";
    }
}
?>
</table>
<div id="update">as of <?php echo gmstrftime('%d %b %Y', filemtime('iba.txt')); ?></div>
<div id="ltcont">
<div id="lt">
Player: 
<select name="parties" id="parties">
<?php foreach($parties as $party) {
    $party = htmlentities($party);
    $p = $prev->$party;
    if(!$p) $p = 0;
    echo "<option value='$party'";
    if($party == $loser) echo " selected='selected'";
    echo ">$party ($p)</option>\n";
} ?>
</select>
<br>
<div id="row">
<a id="cancel" href="#" onclick="return cancel();">Cancel</a>
<a id="bob" href="#" onclick="return askBob();">Ask Bob</a>
</div>
Now: <span id="now"><?php echo $holdings->$loser; ?>zm</span><br>
Change: <span id="total">--</span><br>
<textarea id="stuff">
</textarea>
</div>
</div>
<script>
var data = <?php echo json_encode($data); ?>;
var userzm = <?php echo $holdings->$loser; ?>;
var prevs = <?php echo json_encode($prev); ?>;
var order = <?php echo json_encode($order); ?>;
var holdings = <?php echo json_encode($holdings); ?>;
</script>
</div>
<script src="rates.js?<?php echo @filemtime('rates.js'); ?>">
</script>
</body>
</html>
