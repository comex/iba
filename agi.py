import re, sys, os, shutil, email.Utils, datetime
#!/usr/bin/env python
# Note: time.py is a really bad name
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
aliases = {
    'C-walker': 'Walker',
}
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
    'Drop your Weapon': 'DyW',
    'Discard Picking': 'DP',
    'Justice Ball': 'J.Ball',
    'Penalty Box': 'PB',

    'X Point': 'XP',
    'Y Point': 'YP',
    'Medal': 'Medal',
}
abbrevs2 =  dict(((v, k) for k, v in abbrevs.items()))
iba_txt_file = 'iba.txt'
iba_txt_format = 2

class iba_report:
    DELIM = '\n\n===============================================================================\n\n'
    datefmt = '%d %B %Y %H:%M:%S'
    prev2rate = [1.00, 1.00, 1.00, 1.00, 0.90, 0.90, 0.90, 0.80, 0.80, 0.80, 0.73, 0.62, 0.50, 0.38, 0.26, 0.18, 0.12, 0.08, 0.05, 0.03, 0.01]
    def __init__(self):
        global iba_txt_file
        name = iba_txt_file
        iba = '\n' + open(name).read().strip()
        self.sections = iba.split(self.DELIM)
        self.sections.pop(0)
        self.ox = int('Offers' in self.sections[2])
        self.totals = []

    def read_all(self):
        self.read_holdings()
        self.read_rates()
        self.read_history()
        self.parse_history()
        self.read_contract()

    def write_all(self):
        self.write_holdings()
        self.write_rates()
        self.write_history()

    def read_holdings(self):
        holdings = {}
        ibap = []
        for hol in self.sections[1].split('\n'):
            if '      ' in hol and 'Nickname' not in hol:
                person, zm = re.split('  +', hol)
                if person[0] == '*':
                    person = person[1:]
                    ibap.append(person)
                holdings[person] = int(zm)
        self.holdings = holdings
        self.ibap = ibap

    def write_holdings(self):
        self.sections[1] = '''
Current Holdings:

Nickname                     zm
---------------------------------
%s

* IBA party

All IBA parties are listed.  All other persons have no zm.
        '''.strip() % '\n'.join( (('*' if person in self.ibap else '') + person).ljust(29) + str(zm) for person, zm in sorted(self.holdings.items(), key=lambda a: a[0].lower()))

    def read_rates(self):
        rates = []
        rdict = {}
        for rate in self.sections[2+self.ox].split('\n'):
            if re.search('[0-9]', rate):
                r = re.split('   +', rate)
                if iba_txt_format == 1:
                    r = map(str.strip, (rate[:12], rate[12:26], rate[26:]))
                else:
                    r = map(str.strip, (rate[:16], rate[16:30], rate[30:]))
                if r[0] == 'Drop your Wea..': r[0] = 'Drop your Weapon'
                r = [r[0], int(r[1]), int(r[2]) if r[2] != '' else 0]
                r.append(r[2])
                rates.append(r)
                rdict[r[0]] = r[1]
            else:
                rates.append(rate)
        self.rates = rates
        self.rdict = rdict
    
    def write_rates(self):
        a = []
        for i in self.rates:
            if isinstance(i, basestring):
                a.append(i)
            else:
                if i[0] == 'Drop your Weapon': i[0] = 'Drop your Wea..'
                a.append( (i[0].ljust(16) + str(i[1]).ljust(14) + str(i[2]) * (i[2] != 0)).rstrip() )
        self.sections[2+self.ox] = '\n'.join(a)

    def lookup_rate(self, x, change_amt=0):
        for a in self.rates:
            if type(a) == list and a[0] == x:
                a[2] = a[2] + change_amt
                if a[2] < 0:
                    raise ValueError('I ran out of %s (there were only %d)' % (x, a[3]))
                return a[1]
        raise KeyError(x)
    
    def read_history(self):
        self.history = self.sections[3+self.ox]
    
    def parse_times(self, n, translate=True):
        # Parsers something like 5*Xc and returns ('X crop', 5)
        n = n.strip().split('*')
        if len(n) > 1:
            p = int(n[0])
            q = n[1]
        else:
            p = 1
            q = n[0]
        if translate: q = abbrevs2.get(q, q)
        return p, q

    def parse_history(self, limit=True, want_actions=False, want_holdings=False):
        if limit:
            monday = datetime.datetime.utcnow()
            monday = (monday - datetime.timedelta(days=monday.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        if want_actions:
            actions = []
        elif want_holdings:
            holdings = {}

        hist = ''
        when = None

        history = self.history
        history = re.sub('\[[^\]]+\]', lambda a: ' ' * len(a.group(0)), history)

        for line in history.split('\n'):
            if line.startswith('*'): continue
            if iba_txt_format == 1:
                a, b = line[:24].strip(), line[24:].strip()
            else:
                a, b = line[:27].strip(), line[27:].strip()
            if a != '' and a != 'History:' and '[' not in a:
                when = datetime.datetime.strptime(a, self.datefmt)
            if b != '' and (not limit or when >= monday):
                hist += b + '\n' 
        hist = hist.replace(',\n', ', ')
        hist = hist.replace(' +', '\n+')
        hist = hist.replace(' -', '\n-')
        prev = {}
        for line in hist.split('\n'):
            line = line.strip()
            if line == '' or line[0] == '[': continue
            if want_actions and line[0] in ('+', '-'):
                amt = int(line[:line.find('zm')])
                actions.append((actor, amt))
            if line[0] == '+' or (want_holdings and line[0] == '-'):
                m = re.search('\((.*)\)', line)
                if not m: continue
                for n in m.group(1).split(','):
                    p, q = self.parse_times(n, want_holdings)
                    if want_holdings:
                        holdings[q] = holdings.get(q, 0) + (-1 if line[0] == '-' else 1) * p
                    if line[0] == '+':
                        prev[actor] = prev.get(actor, 0) + p
            elif line[0] == '-':
                pass
            else:
                actor = line

        self.prev = prev
        if want_actions:
            return actions
        elif want_holdings:
            for m in re.findall(re.compile('\[IBA ([^\]]*)\]', re.S), self.history):
                mms = re.split('([\+-])', m)
                for i in xrange(1, len(mms), 2):
                    sign = mms[i]
                    assert sign in ('-', '+')
                    mm = mms[i+1]
                    for mmm in re.split('[ ,]+', mm.strip()):
                        p, q = self.parse_times(mmm, True)
                        holdings[q] = holdings.get(q, 0) + (-1 if sign == '-' else 1) * p
            return holdings

    def write_history(self):
        self.sections[3+self.ox] = self.history

    def read_contract(self):
        self.contract = self.sections[4+self.ox]

    def test_retrieve_now(self):
        # Make it actually now.  For testing.
        self.now = datetime.datetime.utcnow()

    def retrieve_now(self):
        vr = sys.stdin.read()
        lines = vr.split('\n')
        dt = [lines[i+1] for i in xrange(len(lines)) if lines[i].find('by yzma.clarkk.net') != -1 or lines[i].find('by pzk37') != -1 or lines[i].find('by yoyo') != -1][0]
        self.now = datetime.datetime.utcfromtimestamp(email.Utils.mktime_tz(email.Utils.parsedate_tz(dt[dt.index(';')+2:])))
    

    def transact(self, typ, asts, sorted_mode=None): # typ is 'deposit'/'withdraw'
        total = 0
        sore = []
        stuff = []
        for ast in asts.split(','):
            ii = 1
            if '*' in ast:
                ast = ast.split('*')
                ii, ast = int(ast[0]), ast[1].strip()
            stuff.append((ii, ast))
        for ii, ast in (sorted(stuff, key=lambda (a, b): b) if sorted_mode else stuff):
            if ii > 1:
                sore.append('%d*%s' % (ii, abbrevs.get(ast, ast)))
            else:
                sore.append(abbrevs.get(ast, ast))
            ast = abbrevs2.get(ast, ast)
            for i in xrange(ii):
                if typ == 'deposit':
                    p = self.prev.get(self.person, 0)
                    if p >= 21:
                        rmul = 0
                    else:
                        rmul = self.prev2rate[p]
                    self.prev[self.person] = p + 1
                else:
                    rmul = -1
                erate = round(rmul * self.lookup_rate(ast, 1 if typ == 'deposit' else -1))
                self.holdings[self.person] = self.holdings.get(self.person, 0) + int(erate)
                total += int(erate)
                if self.holdings[self.person] < 0: raise ValueError((self.holdings[self.person], self.person))
        total = ('+' * (typ == 'deposit')) + str(total) + 'zm'
        self.totals.append((total, sore))

    def finish_transactions(self):
        sores = []
        max_total_length = max(len(a[0]) for a in self.totals)
        for total, sore in self.totals:
            total = (' ' * (max_total_length - len(total))) + total
            b = 28 + len(self.person) + 1 + len(total) + 2
            c = ' ' * b
            sores.append(total + ' (' + wrap(', '.join(sore), 70 - b).replace('\n', '\n' + c) + ')')


        if len(sores) > 0:
            hdr = self.now.strftime(self.datefmt).ljust(27) + self.person + ' '
            hdr2 = '\n' + ' ' * len(hdr)
            self.history += '\n' + hdr + hdr2.join(sores)

    
    def export(self):
        return self.DELIM.join(self.sections) + '\n'



def main_agi(dry=False, nochange=False):
    report = iba_report()
    report.read_all()

    if not nochange:
        report.retrieve_now()
        report.person = raw_input('Person> ')
        while True:
            line = raw_input()
            if line == '': break
            report.transact(*line.strip().split())
        report.finish_transactions()

    report.write_all()
    export = report.export()

    if dry:
        print export
    else:
        shutil.copy('iba.txt', 'iba.txt.old')
        open('iba.txt', 'w').write(export)

def main_agdump():
    import json
    report = iba_report()
    report.read_all()
    contract = report.contract
    contract = re.sub(re.compile('^([XIV]+\. .*)$', re.M), '<b>\\1</b>', contract)
    json.dump((report.rates, report.prev, sorted(report.holdings.keys(), key=str.lower), sorted(report.rdict.keys(), key=lambda a: -report.rdict[a]), contract, report.holdings), sys.stdout)

def main_rehash():
    report = iba_report()
    report.read_all()
    actions = report.parse_history(limit=False, want_actions=True)
    zm = {}
    for actor, amt in actions:
        print (actor, amt)
        actor = aliases.get(actor, actor)
        zm[actor] = zm.get(actor, 0) + amt
    print sorted(zm.items(), key=lambda a: a[0].lower())
    assert zm == report.holdings

def main_rehash2():
    report = iba_report()
    report.read_all()
    holdings = report.parse_history(limit=False, want_holdings=True)
    for a in report.rates:
        if type(a) == list:
            ast = a[0]
            mine = holdings.get(ast, 0)
            reports = a[2]
            if reports != mine:
                print '! %s report:%d mine:%d' % (ast, reports, mine)

    print holdings

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.set_defaults(mode="agi")
    
    parser.add_option("--agi", action="store_const", dest="mode", const="agi")
    parser.add_option("--agdump", action="store_const", dest="mode", const="agdump")
    parser.add_option("--rehash", action="store_const", dest="mode", const="rehash")
    parser.add_option("--rehash2", action="store_const", dest="mode", const="rehash2")

    parser.add_option("-d", "--dry-run", action="store_true", dest="dry", default=False)
    parser.add_option("-n", "--no-change", action="store_true", dest="nochange", default=False)

    parser.add_option("-f", "--file", action="store", type="string", dest="filename", default="iba.txt")
    parser.add_option("-t", "--format", action="store", type="int", dest="format", default=2)

    options, args = parser.parse_args()

    iba_txt_file = options.filename
    iba_txt_format = options.format
    
    if options.mode == 'agi':
        main_agi(options.dry, options.nochange)
    elif options.mode == 'agdump':
        main_agdump()
    elif options.mode == 'rehash':
        main_rehash()
    elif options.mode == 'rehash2':
        main_rehash2()
    else: raise
