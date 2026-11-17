b1 = open(r'D:\_claude_work\Kasymova\Kasymova_v9.lir', 'rb').read()
b2 = open(r'D:\_claude_work\Kasymova\_old_versions\Kasymova_R_1611_2230.lir', 'rb').read()
print(b1[60:100]); print(b2[60:100])
n = min(len(b1), len(b2))
def first_diff(a, b, start):
    step = 1 << 16
    k = start
    while k < n:
        if a[k:k+step] != b[k:k+step]:
            for j in range(k, min(k+step, n)):
                if a[j] != b[j]:
                    return j
        k += step
    return None
d1 = first_diff(b1, b2, 100)
print('first diff after header:', d1)
# from the end
r1, r2 = b1[::-1], b2[::-1]
e = first_diff(r1, r2, 0)
print('common suffix length:', e, ' => region A', d1, len(b1)-e, ' region B', d1, len(b2)-e)
p1 = int(b1[68:84], 16) if b1[60:68] == b'Preview=' else None
p2 = int(b2[68:84], 16) if b2[60:68] == b'Preview=' else None
print('preview offsets', p1, p2, len(b1)-p1, len(b2)-p2)
# context around first diff
import binascii
print(b1[d1-40:d1+80]); print(b2[d1-40:d1+80])
