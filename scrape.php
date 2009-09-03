<?php
if(0) {
    header('Content-Type: text/plain');
    readfile('scrape.txt');
    die();
}
$fp = fopen("http://nomic.bob-space.com/agorareport.aspx?contract=All%20Decks", "r");
$cards = array();
$mode = 0;
while($line = fgets($fp)) {
    $line = trim($line);
    if($mode == 0) {
        if($line == '-------------') {
            $mode = 1;
        }
    } else if($mode == 1) {
        if($line == '') {
            $mode = 2;
        } else {
            preg_match('!^([^\(]+) \([^\)]+\)( x([0-9]+))?!', $line, $matches);
            $card = $matches[1];
            $cards[$cur][$card] = $matches[3] ? intval($matches[3]) : 1;
        }
    } else if($mode == 2) {
        if($line == '') break;
        $cur = $line;
        $cards[$cur] = array();
        $mode = 1;
    }
}
fclose($fp);

$fp = fopen("http://nomic.bob-space.com/agorareport.aspx?contract=Scorekeepor", "r");
while($line = fgets($fp)) {
    if(preg_match('/^All other players have/', $line)) break;
    if(!preg_match('/(.*) +([0-9]+)\+ *([0-9]+)i/U', $line, $matches)) continue;
    $cards[$user]['X Point'] = intval($matches[1]);
    $cards[$user]['Y Point'] = intval($matches[2]);
}
fclose($fp);

$fp = fopen("http://nomic.bob-space.com/agorareport.aspx?contract=AAA", "r");
$mode = false;
while($line = fgets($fp)) {
    $line = trim($line);
    if(!$mode) {
        if($line != '' && str_replace('-', '', $line) == '') $mode = true;
        continue;
    }
    if($line == '') break;
        
    
    $p = trim(substr($line, 0, 19));
    $stuff = preg_split('/\s+/', substr($line, 19));
    $ar = array('0 Crop', '1 Crop', '2 Crop', '3 Crop', '4 Crop', '5 Crop', '6 Crop', '7 Crop', '8 Crop', '9 Crop', 'X Crop', 'WRV');
    for($i = 0; $i < count($ar); $i++) {
        $cards[$p][$ar[$i]] = intval($stuff[$i]);
    }
    break;
}
header('Content-Type: text/plain');
echo json_encode($cards) . "\n";
?>