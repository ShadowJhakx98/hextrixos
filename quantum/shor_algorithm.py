import numpy as np

def simulate_shor_algorithm(n: int, a: int) -> int:
    def quantum_period_finding(a, N):
        x, y = a, 1
        r = 0
        while y != 1:
            x = (x * a) % N
            y = (y * a) % N
            r += 1
        return r

    if n % 2 == 0:
        return 2

    r = quantum_period_finding(a, n)

    if r % 2 != 0:
        return simulate_shor_algorithm(n, a + 1)

    factor = np.gcd(a**(r // 2) - 1, n)
    if factor == 1 or factor == n:
        return simulate_shor_algorithm(n, a + 1)

    return factor
