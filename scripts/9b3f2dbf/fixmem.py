import sys
p = sys.argv[1]
b = open(p, 'rb').read()
BS = bytes([92])  # backslash
fixes = [(b'\rvbi', BS + b'rvbi'), (b'\rb_', BS + b'rb_'), (bytes([8]) + b'10_rebar', BS + b'b10_rebar')]
n = 0
for a, c in fixes:
    n += b.count(a); b = b.replace(a, c)
open(p, 'wb').write(b)
bad = [i for i, ch in enumerate(b) if ch < 32 and ch not in (9, 10, 13)]
lone_cr = [i for i in range(len(b) - 1) if b[i] == 13 and b[i + 1] != 10]
print('fixed', n, 'control', len(bad), 'lone CR', len(lone_cr))
