import re, sys, os, shutil, email.Utils, datetime, json, hashlib

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
rdict = {}
for rate in sections[2+ox].split('\n'):
    if re.search('[0-9]', rate):
        r = re.split('   +', rate)
        r = map(str.strip, (rate[:16], rate[16:30], rate[30:]))
        r = [r[0], int(r[1]), int(r[2]) if r[2] != '' else 0]
        rates.append(r)
        if r[0] == 'Drop your Wea..': r[0] = 'Drop your Weapon'
        rdict[r[0]] = r[1]
    else:
        rates.append(rate)
monday = datetime.datetime.utcnow()
monday = (monday - datetime.timedelta(days=monday.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

datefmt = '%d %B %Y %H:%M:%S'
hist = ''
when = None
for line in sections[3+ox].split('\n'):
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

contract = sections[4+ox]

contract = re.sub(re.compile('^([XIV]+\. .*)$', re.M), '<b>\\1</b>', contract)

json.dump((rates, prev, sorted(holdings.keys(), key=str.lower), sorted(rdict.keys(), key=lambda a: -rdict[a]), contract, holdings), sys.stdout)
print
