<style>
body {
    background-color: #424242;
    font-family: Verdana;
    font-size: 11px;
}
#tab {

}
#tab td, th {
    background-color: #606060;
    color: #81ffa5;
    font-family: Verdana;
    font-size: 11px;
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
    border-color: #404040;
    color: #ffa9af;
    height: 200px;
}
#parties {
    background-color: #606060;
    color: #ffffff;
    border-color: #404040;
}
</style>
<?php
if(@filemtime('.agd.cache') < max(@filemtime('agdump.py'), @filemtime('iba.txt'))) {
    passthru('python agdump.py 2>&1 > .agd.cache');
}
list($rates, $prev, $parties, $order) = json_decode(file_get_contents('.agd.cache'));
?>
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
            echo "<tr><td colspan='5'" . ($rated ? "" : " id='aaa'") . "><b>" . htmlentities(substr($rate, 3)) . "</b>";
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
    echo "<option value='$party'>$party</option>\n";
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
function fixTotals() {
    var stuff = '';
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
        stuff += 'I ' + (minev < 0 ? 'deposit' : 'withdraw') + ' ' + (ab > 1 ? (ab + ' * ') : 'a ') + data[md][0] + ' for ' + Math.abs(a) + 'zm.\n';
    }
    document.getElementById('total').innerHTML = (total > 0 ? '+' : '') + total + 'zm';
    document.getElementById('stuff').value = stuff;
}

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
