import numpy as np
from src.utils.constants import K_E, SOFTENING


class PointCharge:
    def __init__(self, q, position):
        self.q = float(q)                                  # [C]
        self.position = np.asarray(position, dtype=float)  # [m], shape (3,)


class ElectricField:
    """점전하들의 중첩으로 E(r)을 계산."""

    def __init__(self, charges=None):
        self.charges = charges or []

    def add(self, charge):
        self.charges.append(charge)

    def evaluate(self, r):
        """
        r: 위치 배열, shape (..., 3)
        return: 같은 shape의 E 벡터 [V/m]
        """
        r = np.asarray(r, dtype=float)
        E = np.zeros_like(r)
        for c in self.charges:
            dr = r - c.position                                    # (..., 3)
            r2 = np.sum(dr**2, axis=-1, keepdims=True) + SOFTENING**2
            E = E + K_E * c.q * dr / r2**1.5
        return E

    def potential(self, r):
        """전위 V(r) [V] — 검증용."""
        r = np.asarray(r, dtype=float)
        V = np.zeros(r.shape[:-1])
        for c in self.charges:
            dr = r - c.position
            rmag = np.sqrt(np.sum(dr**2, axis=-1) + SOFTENING**2)
            V = V + K_E * c.q / rmag
        return V