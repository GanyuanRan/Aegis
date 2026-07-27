from quota import remaining


assert remaining(10, 3) == 7
assert remaining(10, 10) == 0
