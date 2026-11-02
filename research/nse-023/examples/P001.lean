/- Packet P-001 — adapter example, compiled against batteries_fork pin
   36cc05ca2d0e469bfbeea9437f460e19238e885e (toolchain v4.34.0-rc1).
   Fleet claim (notation spec, (G, ∘) frame): composition is associative.
   Prefetch at the pin found no Batteries-native lemma (comp_assoc: 0 hits),
   so this adapter states and proves the claim itself; authorship is the
   packet's own. -/
import Batteries

/-- Adapter lemma: function composition is associative. -/
theorem fleet_comp_assoc {α β γ δ : Type*} (f : γ → δ) (g : β → γ) (h : α → β) :
    (f ∘ g) ∘ h = f ∘ (g ∘ h) := by
  funext x
  rfl

#print axioms fleet_comp_assoc
