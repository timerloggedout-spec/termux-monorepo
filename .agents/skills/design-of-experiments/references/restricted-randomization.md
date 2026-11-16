# Restricted randomization and dependence
Blocks group comparable units to control nuisance variation; randomize treatments within blocks when that matches assignment. Check block/treatment confounding before release. Do not create blocks by sorting a fully randomized CSV after design generation.

Split plots assign hard-to-change factors to whole plots and easy-to-change factors within them. Whole-plot effects need whole-plot replication and the corresponding error stratum. Treating all subplot observations as independent usually understates uncertainty for whole-plot factors.

Cluster experiments assign treatments to sites, schools, firms, households, or other groups. Analyze assignment-level dependence; more people in one cluster do not replace more independently randomized clusters. A simple equal-size design-effect approximation is 1+(m-1)*ICC, but few clusters, unequal sizes, baseline adjustment, and non-Gaussian outcomes require more specific calculations.

Repeated measures require covariance modeling or justified unit-level summaries. Crossovers additionally need period, carryover, and washout reasoning. The bundled unrestricted-randomization tools do not validate these structures; hand off to a qualified statistical implementation.
