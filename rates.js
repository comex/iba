function getXmlHttp() {
    var xhr = null;
    try {
        xhr = new ActiveXObject("Msxml2.XMLHTTP");
    } catch(e){
        try {
            xhr = new XMLHttpRequest();
        } catch(e){}
    }
    return xhr;
}
function grabPage(url, callback) {
    var xhr = getXmlHttp();
    if(callback) xhr.onreadystatechange = function() {
        if(xhr.readyState == 4) callback(xhr.responseText);
    }
    xhr.open('GET', url);
    xhr.send(null);
}
var users = null;
var user = null;
var bobmode = false;
function c(x, md, all) {
    var banks = document.getElementById('banks-'+md);
    var mine = document.getElementById('mine-'+md);
    var bankv = data[md][2];
    var minev = data[md][3];
    var u;
    bankv -= x;
    minev += x;

    if(bankv < 0) return;
    
    if(user) {
        u = user[md];
        if(!u) u = 0;
        if(u + minev < 0) return;    
    }
    

    banks.innerHTML = bankv == 0 ? '' : bankv;
    if(user) {
        mine.className = 'mine mirate';
        var v = u + minev;
        mine.innerHTML = v == 0 ? '' : v;
    } else if(minev < 0) {
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

    if(!all) {
        fixLeft();
        fixTotals();
    }
}
function call() {
    for(var md in data) {
        c(0, md, true);
    }
    fixLeft();
    fixTotals();
}
function cancel() {
    for(var md in data) {
        c(-data[md][3], md, true);
    }
    fixLeft();
    fixTotals();
}
var bob = document.getElementById('bob');
var parties = document.getElementById('parties');
var prev2rate = [1.00, 1.00, 1.00, 1.00, 0.90, 0.90, 0.90, 0.80, 0.80, 0.80, 0.73, 0.62, 0.50, 0.38, 0.26, 0.18, 0.12, 0.08, 0.05, 0.03, 0.01];
var totale = document.getElementById('total');
var stuffe = document.getElementById('stuff');
var cancele = document.getElementById('cancel');
function fixTotals() {
    var deposit = ''; var withdraw = '';
    var prev = prevs[parties.value];
    if(!prev) prev = 0;
    var total = 0;
    var yes = false;
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
            yes = true;
        }
        
        var line = 'I ' + (minev < 0 ? 'deposit' : 'withdraw') + ' ' + (ab > 1 ? (ab + ' * ') : 'a ') + data[md][0] + ' for ' + Math.abs(a) + 'zm.\n';
        if(minev < 0) deposit += line; else withdraw += line;
    }
    if(!yes) {
        totale.innerHTML = '--';
        totale.className = '';
        cancele.style.display = 'none';
    } else {
        cancele.style.display = 'inline';
        var newzm = userzm + total;
        totale.innerHTML = (total >= 0 ? '+' : '') + total + 'zm';
        totale.className = (newzm < 0 ? 'negzm' : (total >= 0 ? 'pos' : 'neg'));
        //totale.innerHTML = //(newzm < 0 ? ('<span class="negzm">'+newzm+'zm</span>') : (newzm+'zm')) + ' (<span class="' + (total >= 0 ? 'pos' : 'neg') + '">' + (total >= 0 ? '+' : '') + total + '</span>)';
    }
    stuffe.value = deposit + withdraw;
}
function cancelBob() {
    bobmode = false;
    updateBob();
}
function updateBob() {
    if(bobmode) {
        var p = parties.value;
        if(p == 'comex') p = 'c.';
        user = users[p];
        if(!user) user = {};
        bob.innerHTML = 'Ask Bob';
        bob.onclick = cancelBob;
        bob.href = '#';
        call();
    } else {
        var ou = user;
        user = null;
        bob.innerHTML = 'Ask Bob';
        bob.onclick = askBob;
        bob.href = '#';
        if(ou) call();
    }
}
var now = document.getElementById('now');
parties.onchange = function() {
    userzm = holdings[parties.value];
    now.innerHTML = userzm + 'zm';
    updateBob();
}
fixTotals();
var lt = document.getElementById('lt');
var tab = document.getElementById('tab');
var aaa = document.getElementById('aaa');
function fixLeft() {
    lt.style.left = tab.clientWidth + 15 + 'px';
    lt.style.top = aaa.offsetTop + tab.offsetTop;
    lt.className = 'lt';
}
fixLeft();
window.onload = fixLeft;
function askBob() {
    bob.innerHTML = 'Asking Bob...';
    bob.href = bob.onclick = null;
    // grabpage
    grabPage('scrape.php', function(text) {
        users = eval('('+text+')');
        bobmode = true;
        updateBob();
    });
}
bob.onclick = askBob
var srs = [
    document.getElementById('sectionrate'),
    document.getElementById('sectioncontract'),
    document.getElementById('sectionreport')
];
var lcs = document.getElementById('links').getElementsByTagName('a');
var curn = 0; 
function go(n) {
    if(n == curn) return;
    for(var i = 0; i < srs.length; i++) {
        srs[i].style.display = (i == n) ? 'block' : 'none';
        lcs[i].className = (i == n) ? 'link linkactive' : 'link linkinactive';
        var ih = lcs[i].innerHTML.replace('[', '').replace(']', '');
        if(i == n) ih = '['+ih+']';
        lcs[i].innerHTML = ih;
    }
    if(n == 0) fixLeft();
    curn = n;
}
function checkHash() {
    var q = window.location.hash.replace('#', '');
    q = parseInt(q);
    go(q?q:0);
}
setInterval(checkHash, 200);
checkHash();
