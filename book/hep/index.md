---
title: High Energy Physics
summary: "Collider physics as it is practised: simulating collisions, modelling detectors, and drawing statistical conclusions from what they record."
---

A collider measurement rests on three pillars. The first is **simulation**: a
chain of Monte Carlo programs that turns a Lagrangian into a list of particles,
then into the signals a detector would record. The second is
**reconstruction**: the algorithms that turn those signals, real or simulated,
into physics objects such as jets, leptons and missing momentum. The third is
**inference**: the statistical machinery that confronts the reconstructed data
with hypotheses and reports what has been learned.

The chapters in this part follow that order. They favour the conventions and
tools used in the projects behind this book (MadGraph5_aMC@NLO, Pythia 8,
Delphes, and likelihood-based inference), but the ideas are general and the
text points out where a convention is a choice rather than a necessity.
