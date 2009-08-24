import re, sys
muls = [1.00, 1.00, 1.00, 1.00, 0.90, 0.90, 0.90, 0.80, 0.80, 0.80, 0.73, 0.62, 0.50, 0.38, 0.26, 0.18, 0.12, 0.08, 0.05, 0.03, 0.01]
bits = open('iba.txt').read().split('\n===============================================================================\n')
rates = {}
for bit in bits:
    bit = bit.strip()
    if not re.match('^Current Rates:', bit): continue
    m = re.findall(re.compile('^(.+?) {3,}([0-9]+)', re.M), bit)
    print m
    for ast, val in m:
        rates[ast.strip()] = float(val.strip())

desc = '1 0 Crop, 7 1 Crop, 0 2 Crop, 2 3 Crop, 2 4 Crop, 2 5 Crop, 2 6 Crop, 1 7 Crop, 4 8 Crop, 13 9 Crop, 4 X Crop'
#desc = '2 X Crop, 3 7 Crop, 2 0 Crop'

asts = []
for ast in desc.split(', '):
    num, ast = ast.split(' ', 1)
    asts += [ast] * int(num)

prev = 0
gain = 0
log = ''
for ast in sorted(asts, reverse=True, key=lambda x: rates[x]):
    log += 'prev=%d\tdeposit %s\t\t' % (prev, ast)
    if prev <= 20:
        x = round(rates[ast] * muls[prev])
        log += 'gained %d * %.02f = %d zm\n' % (rates[ast], muls[prev], x)
        gain += x
    else:
        log += 'no gain\n'
    prev += 1
print 'total: %d zm' % gain
print log
