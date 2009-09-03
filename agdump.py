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
m =  re.findall('^([^\n]*:[0-9][0-9]) +([^\n]*) [\-\+][0-9]+zm \((.*?)\)', sections[3+ox], re.S | re.M)
prev = {}
for when, person, stuff in m:
    when = datetime.datetime.strptime(when, datefmt)
    if when < monday: continue
    for n in stuff.split(','):
        n = n.strip().split('*')
        if len(n) > 1:
            p = int(n[0])
        else:
            p = 1
        prev[person] = prev.get(person, 0) + p


contract = sections[4+ox]

contract = re.sub(re.compile('^([XIV]+\. .*)$', re.M), '<b>\\1</b>', contract)

json.dump((rates, prev, sorted(holdings.keys(), key=str.lower), sorted(rdict.keys(), key=lambda a: -rdict[a]), contract, holdings), sys.stdout)
print
