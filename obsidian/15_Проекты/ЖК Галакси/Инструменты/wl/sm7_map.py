# См-7 (axis 1) from analog См-6 (4.21/4.22): pieces analog (rel. analog axis A) -> ours (rel. А/1)
A_ = [(-3125, -125), (-125, -125), (3175, 3175), (7175, 5750), (11600, 17100), (15375, 20375), (17875, 22875)]
def pairs(X, A):           # absolute pairs for a sheet whose analog axis A is at sheet x = A
    return [[X + A + a, X + A + b] for a, b in A_]
