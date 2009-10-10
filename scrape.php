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
            $cards[$cur][strtolower($card)] = $matches[3] ? intval($matches[3]) : 1;
        }
    } else if($mode == 2) {
        if($line == '') break;
        $cur = strtolower($line);
        $cards[$cur] = array();
        $mode = 1;
    }
}
fclose($fp);

$fp = fopen("http://nomic.bob-space.com/agorareport.aspx?contract=Scorekeepor", "r");
while($line = fgets($fp)) {
    if(preg_match('/^All other players have/', $line)) break;
    if(!preg_match('/(.*) +([0-9]+)\+ *([0-9]+)i/U', $line, $matches)) continue;
    $user = strtolower(trim($matches[1]));
    $cards[$user]['x point'] = intval($matches[2]);
    $cards[$user]['y point'] = intval($matches[3]);
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
        
    
    $p = strtolower(trim(substr($line, 0, 19)));
    $stuff = preg_split('/\s+/', trim(substr($line, 19)));
    $ar = array('0 crop', '1 crop', '2 crop', '3 crop', '4 crop', '5 crop', '6 crop', '7 crop', '8 crop', '9 crop', 'x crop', 'wrv');
    for($i = 0; $i < count($ar); $i++) {
        $cards[$p][$ar[$i]] = intval($stuff[$i]);
    }
}
header('Content-Type: text/plain');
echo json_encode($cards) . "\n";
?>
