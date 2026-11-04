(defun c:PLT ( / lay out)
  (setq lay (getenv "PLTLAY") out (getenv "PLTOUT"))
  (setvar "BACKGROUNDPLOT" 0)
  (command "_.-PLOT" "_N" lay "" "" out "_N" "_Y")
  (princ))

