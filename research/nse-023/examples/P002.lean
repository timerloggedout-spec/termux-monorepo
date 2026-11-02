/- Packet P-002 — first Mathlib packet, compiled against mathlib4 pin
   cc8b65263ab8ef05dd813bccd999400f0303fdcc (toolchain v4.36.0-rc2).
   Fleet claim (mapping table, exact row e ↦ 1): the identity changes
   nothing — (1 : Matrix n n α) * M = M.
   Prefetch FOUND the native lemma: Matrix.one_mul
   (Mathlib/Data/Matrix/Mul.lean at the pin). Discharged by citation. -/
import Mathlib

open Matrix

/-- Fleet form of Matrix.one_mul: the matrix identity is a left identity. -/
theorem fleet_matrix_one_mul {n α : Type*} [Fintype n] [DecidableEq n]
    [Semiring α] (M : Matrix n n α) : (1 : Matrix n n α) * M = M :=
  Matrix.one_mul M

#print axioms fleet_matrix_one_mul
