(defun c:NOTS ( / ss i e ed n p s)
  ;; title pages (model x 0..90400, y 0..29800) carry no stamp
  (setq ss (ssget "_X" '((410 . "Model") (0 . "INSERT,TEXT,MTEXT"))) i 0 n 0)
  (repeat (sslength ss)
    (setq e (ssname ss i) ed (entget e) i (1+ i) p (cdr (assoc 10 ed)))
    (if (and (< (car p) 90400) (> (car p) 0) (< (cadr p) 6000) (> (cadr p) 0))
      (progn
        (setq s (cond ((= (cdr (assoc 0 ed)) "INSERT") (cdr (assoc 2 ed))) (T (cdr (assoc 1 ed)))))
        (if (member s '("�����1" "�" "��������� ����")) (progn (entdel e) (setq n (1+ n)))))))
  (princ (strcat "\nNOTS erased " (itoa n)))
  (command "_.QSAVE")
  (princ))
