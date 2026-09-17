# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
"""
The Planck integrand, compiled.

This is the one place in the repository where compiling was the
right answer, and it earned that by measurement rather than by
being the obvious thing to try.

Three earlier attempts at speed did NOT need a compiler. Threads
made the band search seven times slower, because Python holds one
interpreter lock and CPU-bound threads take turns. A 3,400-step
root scan gave identical answers at 200. gravity() was evaluated
1,309,539 times for a constant, and c6() 10,749,440 times for a
pure function of two constants. Every one of those was fixed by not
doing the work, and a compiler would only have made needless work
fast.

What is left is not needless. Planck's law has to be evaluated
2,475,200 times per biosphere run -- 220 quadrature points for each
of 400 spectral bins for each band and each temperature -- and
every one of those evaluations is a different number that something
downstream uses. There is no invariant to hoist and no result to
cache. It is arithmetic that has to happen, which is exactly when a
compiler is worth reaching for.

The Python version stays in engine/radiative.py and the two are
checked against each other, so the compiled path is a second
implementation rather than a replacement.
"""
from libc.math cimport expm1, exp


cdef double _integrand(double nu_cm, double hck_over_kT) noexcept nogil:
    cdef double x = hck_over_kT * nu_cm
    if x > 700.0:
        return 0.0
    return (nu_cm * nu_cm * nu_cm) / expm1(x)


def planck_fraction(double nu_lo, double nu_hi, double T,
                    int n=220,
                    double H=6.62607015e-34,
                    double C=299792458.0,
                    double K=1.380649e-23):
    """Fraction of blackbody emission between two wavenumbers."""
    cdef double hck = H * C * 100.0 / (K * T)
    cdef double full_lo = 1.0, full_hi = 4000.0
    cdef double step_full = (full_hi - full_lo) / n
    cdef double step_part = (nu_hi - nu_lo) / n
    cdef double tot = 0.0, part = 0.0
    cdef int i
    with nogil:
        for i in range(n + 1):
            tot += _integrand(full_lo + i * step_full, hck)
            part += _integrand(nu_lo + i * step_part, hck)
    tot *= step_full
    part *= step_part
    if tot <= 0.0:
        return 0.0
    cdef double f = part / tot
    if f < 0.0:
        return 0.0
    if f > 1.0:
        return 1.0
    return f
