import re, sys, os, shutil, email.Utils, datetime
#!/usr/bin/env python
# Note: time.py is a really bad name
vr = sys.stdin.read()
lines = vr.split('\n')
dt = [lines[i+1] for i in xrange(len(lines)) if lines[i].find('by yzma.clarkk.net') != -1][0]

now = datetime.datetime.utcfromtimestamp(email.Utils.mktime_tz(email.Utils.parsedate_tz(dt[dt.index(';')+2:])))

def wrap(text, width):
    #http://code.activestate.com/recipes/148061/
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )
abbrevs = {
    '0 Crop': '0c',
    '1 Crop': '1c',
    '2 Crop': '2c',
    '3 Crop': '3c',
    '4 Crop': '4c',
    '5 Crop': '5c',
    '6 Crop': '6c',
    '7 Crop': '7c',
    '8 Crop': '8c',
    '9 Crop': '9c',
    'X Crop': 'Xc',

    'Roll Call': 'RC',
    'Debate-o-Matic': 'DoM',
    'Arm-twist': 'At',
    'On the Nod': 'OtN',
    'Kill Bill': 'KB',
    'Lobbyist': 'Lob',
    'Local Election': 'LE',
    'No Confidence': 'NC',
    'Goverment Ball': 'G.Ball',

    'Distrib-u-Matic': 'DuM',
    'Committee': 'Com',
    'Your Turn': 'YT',
    'Presto!': 'P!',
    'Not Your Turn': 'NYT',
    'Supersize Me': 'SM',
    'Shrink Potion': 'SP',
    'Change Ball': 'C.Ball',

    'Absolv-o-Matic': 'AoM',
    'Stool Pigeon': 'SP',
    'Drop your Wea..': 'DyW',
    'Discard Picking': 'DP',
    'Justice Ball': 'J.Ball',
    'Penalty Box': 'PB',

    'X Point': 'XP',
    'Y Point': 'YP',
    'Medal': 'Medal',
}
abbrevs2 =  dict(((v, k) for k, v in abbrevs.items()))
DELIM = '\n\n===============================================================================\n\n'
iba = open('iba.txt').read().strip()
sections = iba.split(DELIM)

ox = int('Offers' in sections[2])

holdings = {}
ibap = []
for hol in sections[1].split('\n'):
    if '      ' in hol and 'Nickname' not in hol:
        person, zm = re.split('  +', hol)
        if person[0] == '*':
            person = person[1:]
            ibap.append(person)
        holdings[person] = int(zm)

rates = []
for rate in sections[2+ox].split('\n'):
    if re.search('[0-9]', rate):
        r = re.split('   +', rate)
        r = map(str.strip, (rate[:16], rate[16:30], rate[30:]))
        r = [r[0], int(r[1]), int(r[2]) if r[2] != '' else 0]
        rates.append(r)
    else:
        rates.append(rate)

def lookupRate(x, damt=None):
    if x == 'Drop your Weapon': x = 'Drop your Wea..'
    for a in rates:
        if type(a) == list and a[0] == x:
            if damt is not None:
                a[2] = a[2] + damt
                assert a[2] >= 0
            return a[1]
    raise KeyError(x)

history = sections[3+ox]

monday = datetime.datetime.utcnow()
monday = (monday - datetime.timedelta(days=monday.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

datefmt = '%d %B %Y %H:%M:%S'
hist = ''
when = None
for line in history.split('\n'):
    if line.startswith('*'): continue
    a, b = line[:27].strip(), line[27:].strip()
    if a != '' and a != 'History:' and '[' not in a:
        when = datetime.datetime.strptime(a, datefmt)
    if b != '' and when >= monday:
        hist += b + '\n' 
hist = hist.replace(',\n', ', ')
hist = hist.replace(' +', '\n+')
hist = hist.replace(' -', '\n-')
prev = {}
for line in hist.split('\n'):
    line = line.strip()
    if line == '' or '[' in line or ']' in line: continue
    if line[0] == '+':
        m = re.search('\((.*)\)', line)
        if not m: continue
        for n in m.group(1).split(','):
            n = n.strip().split('*')
            if len(n) > 1:
                p = int(n[0])
            else:
                p = 1
            prev[actor] = prev.get(actor, 0) + p

    else:
        actor = line

prev2rate = [1.00, 1.00, 1.00, 1.00, 0.90, 0.90, 0.90, 0.80, 0.80, 0.80, 0.73, 0.62, 0.50, 0.38, 0.26, 0.18, 0.12, 0.08, 0.05, 0.03, 0.01]

person = raw_input('Person> ')
sores = []
totals = []
def transact(typ, asts): # typ is 'deposit'/'withdraw'
    total = 0
    sore = []
    for ast in asts.split(','):
        ii = 1
        if '*' in ast:
            ast = ast.split('*')
            ii, ast = int(ast[0]), ast[1].strip()
            sore.append('%d*%s' % (ii, abbrevs.get(ast, ast)))
        else:
            sore.append(abbrevs.get(ast, ast))
        ast = abbrevs2.get(ast, ast)
        for i in xrange(ii):
            if typ == 'deposit':
                p = prev.get(person, 0)
                if p >= 21:
                    rmul = 0
                else:
                    rmul = prev2rate[p]
                prev[person] = p + 1
            else:
                rmul = -1
            erate = round(rmul * lookupRate(ast, 1 if typ == 'deposit' else -1))
            holdings[person] = holdings.get(person, 0) + int(erate)
            total += int(erate)
            if holdings[person] < 0: raise ValueError(holdings[person])
    total = ('+' * (typ == 'deposit')) + str(total) + 'zm'
    totals.append((total, sore))

while True:
    line = raw_input()
    if line == '': break
    transact(*line.strip().split())

max_total_length = max(len(a[0]) for a in totals)
for total, sore in totals:
    total = (' ' * (max_total_length - len(total))) + total
    b = 28 + len(person) + 1 + len(total) + 2
    c = ' ' * b
    sores.append(total + ' (' + wrap(', '.join(sore), 70 - b).replace('\n', '\n' + c) + ')')


if len(sores) > 0:
    hdr = now.strftime(datefmt).ljust(27) + person + ' '
    hdr2 = '\n' + ' ' * len(hdr)
    history += '\n' + hdr + hdr2.join(sores)

sections[1] = '''Current Holdings:

Nickname                     zm
---------------------------------
%s

* IBA party

All IBA parties are listed.  All other persons have no zm.''' % '\n'.join( (('*' if person in ibap else '') + person).ljust(29) + str(zm) for person, zm in sorted(holdings.items(), key=lambda a: a[0].lower()))

sections[2+ox] = '\n'.join(i if isinstance(i, basestring) else (i[0].ljust(16) + str(i[1]).ljust(14) + (str(i[2]) * (i[2] != 0))).rstrip() for i in rates)

sections[3+ox] = history

shutil.copy('iba.txt', 'iba.txt.old')
open('iba.txt', 'w').write(DELIM.join(sections) + '\n')
