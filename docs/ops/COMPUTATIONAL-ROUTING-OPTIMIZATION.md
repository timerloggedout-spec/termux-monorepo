# Computational Routing Optimization

The routing layer now has a dependency-light mathematical control surface in
`scripts/routing_optimization.py`.

## 1. Hard constraints before utility

Eligibility is not a score. Capability, credentials, policy, availability,
quota/cooldown, freshness, and authorization gates remain hard exclusions.

Only after admission may the manager compare utility.

## 2. Pareto frontier

For a route metric vector

`(correctness ↑, latency ↓, cost ↓, risk ↓)`

route A dominates B only when A is no worse on every dimension and strictly
better on at least one. The manager can therefore preserve legitimate
tradeoffs instead of hiding them inside an arbitrary scalar ranking.

Wolfram verification on a representative three-route set produced a frontier
containing all three candidates when each traded correctness for latency/cost.

## 3. Constrained utility

Scalar utility is explicitly subordinate to constraints:

`U = wc*C - wl*L - wcst*Cost - wr*Risk`

A route violating a declared floor/ceiling returns no utility rather than
receiving a large negative score. This prevents unsafe or ineligible routes
from re-entering through optimization.

## 4. Expected Value of Information

`EVI = E[value after information] - value now - experiment cost`

Experiments should run when the expected decision improvement justifies their
request, token, wall-clock, context, duplication, human-attention, quota, and
integration costs.

For example, with a 0.75 probability of improving a decision from value 80
to 100 and a cost of 5, the expected net information value is 10.

## 5. Correlated observations

Repeated retries, cloned tasks, shared incidents, and common upstream failures
must not automatically count as independent evidence. The module exposes an
exchangeable-correlation effective-sample-size weight:

`n_eff = n / (1 + (n-1)rho)`

At rho=1, ten perfectly correlated observations contribute the information
weight of one observation.

## 6. Bayesian uncertainty

The existing Beta-Bernoulli layer remains the empirical posterior engine.
The optimization layer deliberately does not replace it. Posterior means,
intervals, sampling policies, and priors remain separate evidence objects.

For Beta(9,3), Wolfram verification gives mean 0.75 and an exact 95% interval
approximately [0.48224, 0.93978]. The repository's dependency-light fast
interval helper is intentionally only an approximation.

## 7. No provider hierarchy

None of these mechanisms defines a permanent provider rank. They select among
currently eligible treatments under the current objective, evidence snapshot,
uncertainty state, and topology.

That distinction is essential:

`provider identity -> evidence`
`evidence -> belief`
`belief + objective + constraints -> decision`
`decision -> executed route`
`executed route -> new evidence`
