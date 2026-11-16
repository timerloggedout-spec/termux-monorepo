# Sources and attribution
These public sources informed the architecture and DOE scope. This package is original synthesis and code, not a redistribution of other repositories' SKILL.md files.

1. Agent Skills specification: https://agentskills.io/specification — frontmatter constraints, directory layout, progressive disclosure, relative resources. Accessed during package construction.
2. Anthropic skill creator: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md — draft/test/review workflow and packaging conventions. Accessed during package construction.
3. NIST/SEMATECH e-Handbook, Process Improvement: https://www.itl.nist.gov/div898/handbook/pri/pri.htm — DOE selection and analysis taxonomy, factorials, response surfaces, blocking, optimal and mixture designs. The chapter landing page was consulted; individual technical derivations in this package are not represented as quotations from that page.

References for further verification: NIST chapter 5 subsections linked from the chapter index; current documentation for the statistical software used for any advanced design. Record the exact source/version actually used for a particular experiment. Do not claim external technical review or independent validation based on this list.

## Applied-analysis bibliography — MVT / hierarchy / monorepo application (Perplexity analysis, owner-supplied 2026-11-15)

Full citation set behind the v2 extension spec stamped on QUE #5310. Numbering A1-A40 preserves the analysis's own citation order.

- A1. NIST 5.1.1 What is experimental design? https://www.itl.nist.gov/div898/handbook/pri/section1/pri11.htm
- A2. Optimizely — Multivariate tests for Web Experimentation https://docs.optimizely.com/web-experimentation/docs/multivariate-tests-for-optimizely-web-experimentation
- A3. timerloggedout-spec/termux-monorepo https://github.com/timerloggedout-spec/termux-monorepo
- A4. NIST 5.5.5 Nested variation / restricted randomization https://www.itl.nist.gov/div898/handbook/pri/section5/pri55.htm
- A5. Statistical Methods in Agriculture and Experimental Biology https://www.jstor.org/stable/2403061?origin=crossref
- A6. Understanding Factorial Designs, Main Effects, and Interaction Effects (PMC) https://pmc.ncbi.nlm.nih.gov/articles/PMC11076936/
- A7. Bayesian Ordinal Analysis of Cereal Growth Stage Data from Oat Trials in Western Australia https://www.semanticscholar.org/paper/ce81812026a8fa254dc680bbd95ecbc6ef46f480
- A8. Modern Experimental Design http://www.tandfonline.com/doi/abs/10.1080/15598608.2007.10411855
- A9. A General Framework for Design of Experiments (NIST/DoD) https://www.dote.osd.mil/Portals/97/pub/presentations/2009/dew/Encl2-NIST.pdf?ver=2019-09-03-104731-493
- A10. Safflower Phenological Development, Thermal Requirements and Seed Yield as Affected by Sowing Dates https://dergipark.org.tr/en/doi/10.17557/tjfc.1998413
- A11. NIST 5.3.3.1 Completely randomized designs https://www.itl.nist.gov/div898/handbook/pri/section3/pri331.htm
- A12. Plot Size by the Variance Comparison Method for 'Gigante' Cactus Pear http://www.ccsenet.org/journal/index.php/jas/article/view/0/41217
- A13. Testing for Interactions in Multivariate Data (bioRxiv) https://www.biorxiv.org/content/10.1101/2025.11.26.690868v1
- A14. SUGI 28 Statistics and Data Analysis https://www.semanticscholar.org/paper/246bf72098b0b4bfd70e3e15cfe780e0b56e22c8
- A15. Split-Plot Designs (Purdue STAT514 lecture notes) https://www.stat.purdue.edu/~zhanghao/STAT514/Lecture_Notes/LectureNotes20-Split-plot-Designs-.html
- A16. Design of Experiments — Complex Designs (Springer) https://link.springer.com/10.1007/978-1-4939-2122-5_14
- A17. Topic 12. The Split-plot Design and its Relatives (Part I) https://www.unh.edu/halelab/ANFS933/Readings/Topic12_Reading1.pdf
- A18. Hierarchical Modeling and Differential Expression Analysis for RNA-seq Experiments with Inbred and Hybrid Genotypes http://link.springer.com/10.1007/s13253-015-0232-3
- A19. Split-Plot Design (Sensory Society wiki) https://www.sensorysociety.org/knowledge/sspwiki/Pages/Split-Plot%20Design.aspx
- A20. Analysis of variance and covariance: how to choose and construct models for the life sciences https://www.tandfonline.com/doi/full/10.1080/02664760902885203
- A21. 5.1: Factorial or Crossed Treatment Designs (LibreTexts) https://stats.libretexts.org/Bookshelves/Advanced_Statistics/Analysis_of_Variance_and_Design_of_Experiments/05:_Multi-Factor_ANOVA/5.01:_Factorial_or_Crossed_Treatment_Designs
- A22. Development of Integrated Optics for the first Principle Analysis of the terahertz Spectrum of Some Biomolecules https://www.semanticscholar.org/paper/521bc2aa6992f8c70166f020d0c76dc234d6b3d1
- A23. Glossary of Optimizely terminology https://docs.optimizely.com/experimentation-strategy/docs/glossary-of-optimizely-terminology
- A24. Optimizing Eriochrome Black T adsorption: Multivariate approach using full factorial Design, Box-Behnken, AI, and DFT https://linkinghub.elsevier.com/retrieve/pii/S138358662401846X
- A25. Multivariate testing (Optimizely glossary) https://www.optimizely.com/optimization-glossary/multivariate-testing
- A26. Performance Evaluation of a Five-Variable Face-Centered Central Composite Design (IIARD) http://iiardjournals.org/abstract?j=IJASMT&pn=Performance%20Evaluation%20of%20a%20Five-Variable%20Face-Centered%20Central%20Composite%20Design%20with%20Full%20and%20Fractional%20Factorial%20Points%20in%20Process%20Optimization&id=58416
- A27. Obama's $60 million dollar experiment (Optimizely field notes) https://www.optimizely.com/field-notes/articles/how-obama-raised-60-million-by-running-a-simple-experiment
- A28. Exploring the correlation between design of experiments and machine learning prediction accuracy in ultra-precision hard turning of AISI D2 with CBN insert https://link.springer.com/10.1007/s00170-025-15186-7
- A29. Distributive randomization: a pragmatic fractional factorial design (BMC Med Res Methodol) https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-024-02191-9
- A30. Multivariate testing vs A/B testing (Optimizely) https://www.optimizely.com/optimization-glossary/multivariate-test-vs-ab-test
- A31. Effects of wax and graphene concentrations on cutting force in drilling GFRP composites (full factorial DOE) https://journals.sagepub.com/doi/10.1177/00219983251341623
- A32. Experiment types in Web Experimentation (Optimizely) https://docs.optimizely.com/web-experimentation/docs/experiment-types-in-web-experimentation
- A33. Multivariate optimization of ultrasound-assisted extraction from robusta coffee fruit peel (factorial design) https://jrespharm.com/abstract.php?id=1754
- A34. Maximize lift with multi-armed bandit optimizations (Optimizely) https://docs.optimizely.com/experimentation-strategy/docs/maximize-lift-with-multi-armed-bandit-optimizations
- A35. Vessel Classification in Maritime Security Using Fractional Factorial Design and ANOVA (IEEE) https://ieeexplore.ieee.org/document/11638129/
- A36. Optimizely Web Experimentation technical overview https://world.optimizely.com/products/web-experimentation/features/
- A37. The precision of fractional factorial designs under randomization https://www.semanticscholar.org/paper/40e90cd8e594f68eaa4f2532eb495c0e8d65995c0e8d65995c
- A38. Key concept video: Multivariate Test (Optimizely Academy) https://academy.optimizely.com/student/page/2233227-key-concept-video-multivariate-test
- A39. Using a Full Factorial Experiment to Optimize the Performance of an Industrial Chemical Process https://rgsa.openaccesspublications.org/rgsa/article/view/12015
- A40. Web Experimentation training (Optimizely Academy) https://academy.optimizely.com/student/catalog/list?category_ids=35116-web-experimentation

