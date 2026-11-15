# Response surfaces
Use a quadratic response model for local approximation, not global truth. The number of coefficients for k factors is 1+k+k(k-1)/2+k. Allocate additional runs for independent error and model checking.

The bundled face-centered CCD includes all corners, axial points with alpha=1, and requested centers. Its axial points remain inside the specified factor box; it is not generally rotatable. A circumscribed rotatable CCD uses different alpha choices and can exceed nominal corner ranges; it is not generated here.

The bundled Box-Behnken design varies every pair at +/-1 with all other coordinates zero, plus centers. It avoids all-factor corners, but this does not imply every run is safe or that boundary prediction is precise. At least three factors are required.

Inspect the quadratic Hessian and stationary point classification before describing an optimum. A stationary point can be a maximum, minimum, or saddle; it can lie outside the feasible region. Use constrained optimization where appropriate and confirm independently at a candidate setting and relevant comparators. Multiresponse desirability weights are value judgments that need stakeholder agreement.
