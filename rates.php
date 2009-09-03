<html>
<head>
<style>
body {
    background-color: #424242;
    font-family: Verdana;
    font-size: 11px;
}
#sectionreport {
    color: #fff;
    white-space: pre;
    font-family: monospace;
    display: none;
}
#sectioncontract {
    color: #fff;
    white-space: pre;
    display: none;
}
#sectionrate {
}
#links {
    margin-bottom: 3px;
}
#links .link {
    border-color: #606060;
    color: #81ffa5;
    text-decoration: underline;
}
#tab {
        
}
#tab td, th {
    background-color: #606060;
    color: #81ffa5;
    font-family: Verdana;
    font-size: 11px;
}
#tab td.ghost {
    padding-top: 3px;
    padding-bottom: 3px;
}
#tab td.rate {
    color: #ffa9af;
    font-weight: bold;
    padding-left: 5px;
}
#tab button {
    background-color: #404040;
    font-weight: bold;
    color: #888; /*#e8646a;*/
    border: 1px solid #777777;
    text-align: center;
    width: 50px;
    margin: 0px;
    padding-top: 2px;
    padding-bottom: 2px;
    cursor: pointer;
}
#tab td.mine {
    font-weight: bold;
}
#tab td.mipos, td.mineg {
    width: 40px;
    text-align: center;
}
#tab td.mipos {
    color: #81ffa5;
}
#tab td.mineg {
    color: #f7a9af;
}
#total.pos {
    font-weight: bold;
    color: #81ffa5;
}
#total.neg {
    font-weight: bold;
    color: #f7a9af;
}
div.lt {
    position: fixed;
    top: 27px;
    background-color: #606060;
    color: #ffa9af;
    border-radius: 3px;
    -moz-border-radius: 3px;
    -webkit-border-radius: 3px;
    padding: 5px; 
}
textarea#stuff {
    background-color: #606060;
    border: 1px solid #404040;
    padding: 1px;
    color: #ffa9af;
    height: 200px;
    font-family: Verdana;
    font-size: 11px;
    margin-top: 5px;
}
#parties {
    background-color: #606060;
    color: #ffffff;
    border: 1px solid #404040;
}
</style>
</head>
<body>
<?php
if(@filemtime('.agd.cache') < max(@filemtime('agdump.py'), @filemtime('iba.txt'))) {
    passthru('python agdump.py 2>&1 > .agd.cache');
}
list($rates, $prev, $parties, $order, $contract) = json_decode(file_get_contents('.agd.cache'));
?>
<div id="links">
<a class="link" href="#0" onclick="go(0);">rate calculator</a>
<a class="link" href="#1" onclick="go(1);">contract</a>
<a class="link" href="#2" onclick="go(2);">report</a>
</div>
<div id="sectionreport">
<?php readfile('iba.txt'); ?>
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
        $md = substr(md5($rate[0]), 0, 4);
        $data[$md] = array($rate[0], $rate[1], $rate[2], 0);
        $banks = $rate[2] == 0 ? '' : $rate[2];
        echo "<tr id='tr-$md'><td>{$rate[0]}</td><td class='rate'>{$rate[1]}</td><td class='rate' id='banks-$md'>{$banks}</td><td class='btab'><button onclick=\"return c(-1,'$md');\">&laquo;</button><button id='ra-$md' onclick=\"return c(1,'$md');\">&raquo;</button></td><td class='mine' id='mine-$md'></td></tr>\n";
    }
}
?>
</table>
<div id="lt">
Player: 
<select name="parties" id="parties">
<?php foreach($parties as $party) {
    $party = htmlentities($party);
    $p = $prev->$party;
    if(!$p) $p = 0;
    echo "<option value='$party'>$party ($p)</option>\n";
} ?>
</select>
<br>
Total: <span id="total">--</span><br>
<textarea id="stuff">
</textarea>
</div>
<script type="text/javascript">
var data = <?php echo json_encode($data); ?>;
function c(x, md) {
    var banks = document.getElementById('banks-'+md);
    var mine = document.getElementById('mine-'+md);
    var bankv = data[md][2];
    var minev = data[md][3];
    
    bankv -= x;
    minev += x;

    if(bankv < 0) return;

    banks.innerHTML = bankv == 0 ? '' : bankv;
    if(minev < 0) {
        mine.className = 'mine mineg';
        mine.innerHTML = minev;
    } else if(minev > 0) {
        mine.className = 'mine mipos';
        mine.innerHTML = '+'+minev;
    } else {
        mine.className = 'mine';
        mine.innerHTML = '';
    }
    data[md][2] = bankv;
    data[md][3] = minev;

    fixLeft();
    fixTotals();
}
var prevs = <?php echo json_encode($prev); ?>;
var parties = document.getElementById('parties');
var prev2rate = [1.00, 1.00, 1.00, 1.00, 0.90, 0.90, 0.90, 0.80, 0.80, 0.80, 0.73, 0.62, 0.50, 0.38, 0.26, 0.18, 0.12, 0.08, 0.05, 0.03, 0.01];
var order = <?php echo json_encode($order); ?>;
var totale = document.getElementById('total');
var stuffe = document.getElementById('stuff');
function fixTotals() {
    var deposit = ''; var withdraw = '';
    var prev = prevs[parties.value];
    if(!prev) prev = 0;
    var total = 0;
    var md; for(var e = 0; md = order[e]; e++) {
        var minev = data[md][3];
        if(minev == 0) continue;
        var rate = data[md][1];
        var a = 0;
        var ab = Math.abs(minev);
        for(var i = 0; i < ab; i++) {
            var mult;
            if(minev < 0) {
                mult = prev >= 21 ? 0 : -prev2rate[prev];
                prev++;
            } else {
                mult = 1.0;
            }
            var q = Math.round(mult * rate);
            total -= q;
            a -= q;
        }
        
        var line = 'I ' + (minev < 0 ? 'deposit' : 'withdraw') + ' ' + (ab > 1 ? (ab + ' * ') : 'a ') + data[md][0] + ' for ' + Math.abs(a) + 'zm.\n';
        if(minev < 0) deposit += line; else withdraw += line;
    }
    if(total == 0) {
        totale.innerHTML = '--';
        totale.className = '';
    } else {
        totale.innerHTML = (total > 0 ? '+' : '') + total + 'zm';
        totale.className = (total > 0 ? 'pos' : 'neg');
    }
    stuffe.value = deposit + withdraw;
}
parties.onchange = fixTotals;
var lt = document.getElementById('lt');
var tab = document.getElementById('tab');
var aaa = document.getElementById('aaa');
function fixLeft() {
    lt.style.left = tab.clientWidth + 15 + 'px';
    lt.style.top = aaa.offsetTop + tab.offsetTop;
    lt.className = 'lt';
}
fixLeft();
</script>
</div>
<script type="text/javascript">
var srs = [
    document.getElementById('sectionrate'),
    document.getElementById('sectionreport'),
    document.getElementById('sectioncontract')
];
var curn = 0; 
function go(n) {
    for(var i = 0; i < srs.length; i++) {
        srs[i].style.display = (i == n) ? 'block' : 'none';
    }
    if(n == 0) fixLeft();
    curn = n;
}
function checkHash() {
    var q = window.location.hash.replace('#', '');
    if(q) go(parseInt(q));
}
setInterval(checkHash, 200);
checkHash();
</script>
</body>
</html>
