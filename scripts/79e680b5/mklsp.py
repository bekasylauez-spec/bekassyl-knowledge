import sys

def esc(s):
    out = []
    for ch in s:
        if ord(ch) < 128:
            out.append(ch.replace('\\', '\\\\').replace('"', '\\"'))
        else:
            out.append('\\\\U+%04X' % ord(ch))
    return ''.join(out)

ins = ('{\\fSymbol|b0|i1|c2|p18;·@TAB@}'
       'Каменная наброска водобойной части фракции 25–50 мм — 1159 м³ '
       '(1008 м³ с коэффициентом 1,15).\\P')

lsp = r'''(defun c:NABR ( / e ed txt pos anchor ins new out done cand bs n)
  (setq e (handent "1285A9"))
  (setq ed (entget e))
  (setq txt "")
  (foreach p ed (if (= (car p) 3) (setq txt (strcat txt (cdr p)))))
  (setq txt (strcat txt (cdr (assoc 1 ed))))
  (setq anchor "34028-2016.  \\P")
  (setq pos (vl-string-search anchor txt))
  (cond
    ((null pos) (princ "\nNABR: ANCHOR NOT FOUND"))
    ((vl-string-search "U+00B3 (1008" txt) (princ "\nNABR: ALREADY"))
    ((vl-string-search "1159" txt) (princ "\nNABR: ALREADY2"))
    (t
      (setq pos (+ pos (strlen anchor)))
      (setq ins (vl-string-subst (chr 9) "@TAB@" "@INS@"))
      (setq new (strcat (substr txt 1 pos) ins (substr txt (1+ pos))))
      (setq out nil done nil)
      (foreach p ed
        (if (member (car p) '(1 3))
          (if (not done)
            (progn
              (while (> (strlen new) 250)
                (setq cand (substr new 1 250) bs (vl-string-position 92 cand nil t) n 250)
                (if (and bs (> (+ bs 8) 250)) (setq n bs))
                (setq out (cons (cons 3 (substr new 1 n)) out))
                (setq new (substr new (1+ n))))
              (setq out (cons (cons 1 new) out))
              (setq done t)))
          (setq out (cons p out))))
      (if (entmod (reverse out)) (princ "\nNABR: OK") (princ "\nNABR: ENTMOD FAILED"))
      (entupd e)))
  (princ))
'''.replace('@INS@', esc(ins))
open(sys.argv[1], 'w', encoding='ascii').write(lsp)
print(esc(ins))
