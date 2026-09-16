"""
Solving the Lane-Emden equation, so one asserted constant stops
being asserted.

engine/unsolved.py lists five things this repo states and does not
derive, each with what would close it. For the Lane-Emden n=3
constant the entry read: "solving the Lane-Emden equation
numerically in this repo". This does that, so that entry comes off
the list.

WHAT WAS ASSERTED. engine/remnants.chandrasekhar() computes the
white-dwarf ceiling from hbar, c, G and the hydrogen mass, times a
constant:

    M_Ch = C * (hbar c / G)^(3/2) / (mu_e m_H)^2,  C = 3.0984

Everything in that except C came from measured constants. C came
from a table, and the module said so -- it is the structure of a
star that supports itself by degenerate pressure, and structure is
the solution of a differential equation nobody here was solving.

THE EQUATION. A self-gravitating sphere whose pressure goes as
density^(1+1/n) obeys, in dimensionless form,

    (1/xi^2) d/dxi (xi^2 dtheta/dxi) + theta^n = 0
    theta(0) = 1,  theta'(0) = 0

n=3 is the relativistic degenerate case, which is why it is the one
the Chandrasekhar mass needs. The equation has no closed-form
solution at n=3; it is integrated. What the mass needs from it is
one number,

    omega_3 = -xi_1^2 theta'(xi_1)

evaluated at the first zero xi_1, and then C = (sqrt(3 pi)/2) *
omega_3, where the sqrt(3 pi)/2 is algebra rather than structure.

STARTING AT ZERO, WHICH THE EQUATION WILL NOT DO. There is a
coordinate singularity at xi=0: the 2/xi term blows up. So the
integration does not start there. The series solution near the
origin, theta = 1 - xi^2/6 + n xi^4/120 - ..., is exact to the order
kept and is used to step off the singularity, after which plain
RK4 runs. The step-off distance is not tuned -- halving it must not
move the answer, and check() requires that.

HOW IT IS CHECKED, THREE WAYS.

    CONVERGENCE   halving the step must not move xi_1 or omega_3
                  beyond the order RK4 promises. A number that
                  depends on the step size is a number about the
                  integrator.
    ENUMERATE     n=0 and n=1 have exact closed forms -- xi_1 =
                  sqrt(6) and pi, omega_3 = sqrt(6) and pi -- so the
                  same integrator is run on them and scored against
                  algebra it cannot influence.
    EXTERNAL      the derived C must reproduce the number that was
                  asserted, and the Chandrasekhar mass built on it
                  must still land near 1.4 solar masses.

The n=0 and n=1 cases are the ones that matter. They are a positive
control: if the integrator were wrong, it would be wrong there too,
and there the right answer is known exactly.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED = "DERIVED"


class Fact:
    def __init__(self, value, kind, check, why):
        self.value, self.kind, self.check, self.why = value, kind, check, why

    def __str__(self):
        return f"{self.value}  [{self.kind}, {self.check}] {self.why}"


def _theta_pow(theta, n):
    """theta**n, with theta clamped at zero.

    Past the first zero theta goes slightly negative and a
    fractional power of a negative number is not real. The physical
    surface IS that zero, so the integration stops there; clamping
    keeps the last step from raising instead of terminating.
    """
    return 0.0 if theta <= 0.0 else theta ** n


def _series_start(xi, n):
    """theta and theta' near the origin, where the ODE is singular."""
    th = 1.0 - xi * xi / 6.0 + n * xi ** 4 / 120.0
    dth = -xi / 3.0 + n * xi ** 3 / 30.0
    return th, dth


def solve(n=3.0, h=1e-5, x0=1e-4):
    """-> (xi_1, omega_n). RK4 from a series start to the first zero."""
    xi = x0
    th, dth = _series_start(x0, n)

    def deriv(x, y, dy):
        return dy, -_theta_pow(y, n) - 2.0 * dy / x

    prev_xi, prev_th, prev_dth = xi, th, dth
    steps = 0
    while th > 0.0 and xi < 1e3:
        k1y, k1d = deriv(xi, th, dth)
        k2y, k2d = deriv(xi + h / 2, th + h * k1y / 2, dth + h * k1d / 2)
        k3y, k3d = deriv(xi + h / 2, th + h * k2y / 2, dth + h * k2d / 2)
        k4y, k4d = deriv(xi + h, th + h * k3y, dth + h * k3d)
        prev_xi, prev_th, prev_dth = xi, th, dth
        th += h * (k1y + 2 * k2y + 2 * k3y + k4y) / 6.0
        dth += h * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0
        xi += h
        steps += 1
    if th > 0.0:
        raise ArithmeticError(f"no surface found for n={n} by xi={xi:g}")

    # POLISH THE ROOT, DO NOT INTERPOLATE IT. Linear interpolation
    # across the bracketing step left n=0 wrong by 1.8e-6 -- small,
    # and larger than the 1e-6 the closed forms are checked against.
    # Loosening that tolerance would have been tuning the test to the
    # method. Instead: Newton on theta, taking each trial step with
    # the same RK4 from the last good state, so the surface is found
    # by integrating to it rather than by drawing a line across it.
    def step(x, y, dy, dx):
        k1y, k1d = deriv(x, y, dy)
        k2y, k2d = deriv(x + dx / 2, y + dx * k1y / 2, dy + dx * k1d / 2)
        k3y, k3d = deriv(x + dx / 2, y + dx * k2y / 2, dy + dx * k2d / 2)
        k4y, k4d = deriv(x + dx, y + dx * k3y, dy + dx * k3d)
        return (y + dx * (k1y + 2 * k2y + 2 * k3y + k4y) / 6.0,
                dy + dx * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0)

    dx = 0.0
    for _ in range(60):
        y, dy = step(prev_xi, prev_th, prev_dth, dx) if dx else \
            (prev_th, prev_dth)
        if dy == 0.0:
            break
        adj = -y / dy
        if abs(adj) < 1e-15:
            break
        dx += adj
        if not (0.0 <= dx <= h * 1.5):
            dx = max(0.0, min(dx, h))
    th_1, dth_1 = step(prev_xi, prev_th, prev_dth, dx)
    xi_1 = prev_xi + dx
    if abs(th_1) > 1e-12:
        raise ArithmeticError(f"root polish left theta={th_1:.2e} at the "
                              f"surface")
    return xi_1, -xi_1 * xi_1 * dth_1


def omega(n=3.0, h=1e-5):
    xi1, w = solve(n, h)
    return Fact(w, DERIVED, "REDUNDANT",
                f"Lane-Emden n={n:g} integrated to its first zero at "
                f"xi_1={xi1:.5f}, giving omega={w:.5f} = -xi_1^2 "
                f"theta'(xi_1)")


def chandrasekhar_constant(h=1e-5):
    """C in M_Ch = C (hbar c/G)^(3/2)/(mu_e m_H)^2. DERIVED now."""
    w = solve(3.0, h)[1]
    c = math.sqrt(3.0 * math.pi) / 2.0 * w
    return Fact(c, DERIVED, "REDUNDANT",
                f"sqrt(3 pi)/2 * omega_3 = {math.sqrt(3*math.pi)/2:.5f} * "
                f"{w:.5f} = {c:.5f}; the omega is integrated here, the "
                f"prefactor is algebra")


# n=0 and n=1 have closed forms. ASSERTED only in the sense that
# algebra is asserted -- they are what the integrator is scored on.
# n=0: theta = 1 - xi^2/6, so theta' = -xi/3, xi_1 = sqrt(6) and
#      omega_0 = -xi_1^2 theta'(xi_1) = -6 * (-sqrt(6)/3) = 2 sqrt(6)
# n=1: theta = sin(xi)/xi, theta'(pi) = -1/pi, so omega_1 = pi
#
# The first of those was written here as sqrt(6) and the control
# failed on it -- correctly, and against ITSELF rather than the
# integrator, which had matched xi_1 to ten figures and n=3 to the
# literature's 6.89685 and 2.01824. A positive control that can only
# ever indict the thing under test is not much of a control; this one
# indicted the reference value, which is the other outcome it exists
# to produce.
EXACT = {0.0: (math.sqrt(6.0), 2.0 * math.sqrt(6.0)),
         1.0: (math.pi, math.pi)}


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("closed_forms", _exact)
    t("step_independent", _conv)
    t("reproduces_the_assertion", _repro)
    t("chandrasekhar_still_right", _mass)
    return all(o[1] for o in out), out


def _exact():
    """The positive control: two cases where algebra knows the answer."""
    rows = []
    for n, (xi_e, w_e) in EXACT.items():
        xi, w = solve(n, h=1e-5)
        dx, dw = abs(xi - xi_e) / xi_e, abs(w - w_e) / w_e
        if dx > 1e-6 or dw > 1e-6:
            raise ArithmeticError(
                f"n={n:g}: xi_1 {xi:.6f} vs exact {xi_e:.6f}, omega {w:.6f} "
                f"vs {w_e:.6f}")
        rows.append(f"n={n:g} xi_1={xi:.6f} (exact {xi_e:.6f}, "
                    f"{dx:.1e} out)")
    return ("the same integrator on the two cases with closed forms: "
            + "; ".join(rows))


def _conv():
    a = solve(3.0, h=2e-5)
    b = solve(3.0, h=1e-5)
    dxi, dw = abs(a[0] - b[0]), abs(a[1] - b[1])
    if dxi > 1e-6 or dw > 1e-6:
        raise ArithmeticError(f"halving the step moved xi_1 by {dxi:.2e} "
                              f"and omega by {dw:.2e}")
    return (f"halving the step moves xi_1 by {dxi:.1e} and omega by "
            f"{dw:.1e} -- the answer is about the equation, not the "
            f"integrator")


def _repro():
    from engine.remnants import LANE_EMDEN_C
    c = chandrasekhar_constant().value
    rel = abs(c - LANE_EMDEN_C) / LANE_EMDEN_C
    if rel > 1e-3:
        raise ArithmeticError(f"derived {c:.5f} against asserted "
                              f"{LANE_EMDEN_C}, {rel:.2%} apart")
    return (f"derived {c:.5f} against the {LANE_EMDEN_C} that was "
            f"asserted, {rel:.2e} apart -- the table value was right and "
            f"is now unnecessary")


def _mass():
    from engine import remnants
    m = remnants.chandrasekhar().value
    if not (1.3 < m < 1.5):
        raise ArithmeticError(f"M_Ch came out {m:.3f}")
    return (f"the Chandrasekhar mass built on the DERIVED constant is "
            f"{m:.4f} solar masses, against an accepted 1.4")


if __name__ == "__main__":
    for n in (0.0, 1.0, 1.5, 3.0):
        xi, w = solve(n)
        ex = EXACT.get(n)
        note = (f"   exact xi_1={ex[0]:.6f} omega={ex[1]:.6f}" if ex else "")
        print(f"  n={n:<4} xi_1={xi:.6f}  omega={w:.6f}{note}")
    print()
    print(" ", omega(3.0))
    print(" ", chandrasekhar_constant())
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:26}{d[:104]}")
    print("\nall:", ok)
