# Stats helpers (standard library only)

Paste into `execute_code` and adapt. pandas and numpy are available; scipy is not assumed.

```python
import math
from math import comb, erfc, sqrt

def wilson(k, n, z=1.96):
    """95% Wilson interval for a proportion k/n. Returns (low, high) as fractions."""
    if n == 0: return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (c - h, c + h)

def two_prop_z(k1, n1, k2, n2):
    """Two-sided z-test for the difference of two proportions. Returns (diff, p_value)."""
    p1, p2 = k1/n1, k2/n2
    pp = (k1 + k2) / (n1 + n2)
    se = sqrt(pp*(1-pp)*(1/n1 + 1/n2))
    if se == 0: return (p1 - p2, 1.0)
    z = (p1 - p2) / se
    return (p1 - p2, erfc(abs(z)/sqrt(2)))

def fisher_exact_2x2(a, b, c, d):
    """Two-sided Fisher exact p-value for [[a, b], [c, d]]. Use when any cell is under 5."""
    r1, r2, c1, n = a+b, c+d, a+c, a+b+c+d
    def pr(x): return comb(c1, x) * comb(n-c1, r1-x) / comb(n, r1)
    p_obs = pr(a)
    lo, hi = max(0, r1-(n-c1)), min(r1, c1)
    return min(1.0, sum(pr(x) for x in range(lo, hi+1) if pr(x) <= p_obs + 1e-12))

def diff_ci(k1, n1, k2, n2, z=1.96):
    """Approximate 95% interval for p1 - p2 (Wald)."""
    p1, p2 = k1/n1, k2/n2
    se = sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
    return (p1-p2 - z*se, p1-p2 + z*se)
```

Example: `wilson(31, 47)`, `two_prop_z(31, 47, 12, 40)`, `fisher_exact_2x2(31, 16, 12, 28)`.
For means (a 1-5 rating compared across groups), report mean, SD and n per group, and the difference with an approximate interval of `1.96 * sqrt(s1**2/n1 + s2**2/n2)`; say it is approximate when a group has under 30 responses.
