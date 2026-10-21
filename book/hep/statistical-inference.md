---
title: Statistical Inference
summary: "Likelihood-based inference as practised at colliders: building a statistical model, profiling nuisance parameters, and reporting limits, significances and measurements."
status: in-preparation
references:
  cowan2011: "G. Cowan, K. Cranmer, E. Gross and O. Vitells, *Asymptotic formulae for likelihood-based tests of new physics*, Eur. Phys. J. C **71** (2011) 1554, [arXiv:1007.1727](https://arxiv.org/abs/1007.1727)."
  read2002: "A. L. Read, *Presentation of search results: the CL<sub>s</sub> technique*, J. Phys. G **28** (2002) 2693."
  histfactory: "K. Cranmer, G. Lewis, L. Moneta, A. Shibata and W. Verkerke, *HistFactory: a tool for creating statistical models for use with RooFit and RooStats*, CERN-OPEN-2012-016 (2012)."
  pyhf: "L. Heinrich, M. Feickert, G. Stark and K. Cranmer, *pyhf: pure-Python implementation of HistFactory statistical models*, J. Open Source Softw. **6** (2021) 2823."
---

## The statistical model

Every collider result begins with a likelihood: a probability model for the
observed data as a function of parameters of interest and nuisance parameters.
The binned template likelihood in the HistFactory form [@histfactory], with
its normalisation factors, shape systematics and auxiliary measurements, is
the workhorse of searches and measurements alike, and pure-Python
implementations such as pyhf [@pyhf] make it easy to build, inspect and share.
The section will define the model and the conventions for constraint terms.

## Profile likelihood tests

Hypothesis tests are built from the profile likelihood ratio, with nuisance
parameters fitted to their best values under each hypothesis. The asymptotic
formulae of Cowan, Cranmer, Gross and Vitells [@cowan2011] give closed-form
distributions for the test statistics and the Asimov dataset for expected
results. The section covers the test statistics for discovery and for upper
limits, their asymptotic distributions, and when to fall back to toys.

## Limits, significances and intervals

Exclusion limits at colliders are quoted with the CL<sub>s</sub> prescription
[@read2002], which protects against excluding a signal the experiment is not
sensitive to. The section explains the construction, the expected limit bands,
the distinction between model-independent and model-dependent limits, and the
reporting of confidence intervals for measured parameters.

## Practice

The closing section gathers the practical checks that make an inference
trustworthy: pulls and constraints of the nuisance parameters, the ranking of
systematic uncertainties by their impact, the behaviour of the likelihood
scan, and the reproducibility of the fit itself.

## Further reading

pyhf
:   <https://pyhf.readthedocs.io/>. The documentation doubles as a readable
    specification of the HistFactory model, and the *scikit-hep* tools built
    around it (cabinetry for building workspaces, hepstats for inference)
    are linked from there.

RooFit and RooStats
:   <https://root.cern/manual/roofit/>. The reference implementation of the
    HistFactory models and the profile-likelihood machinery used in most LHC
    results; its tutorials show the standard test statistics in code.

Particle Data Group review on statistics
:   <https://pdg.lbl.gov/>. The *Statistics* review is the agreed summary of
    the conventions (confidence intervals, limits, significance) that collider
    results follow; the *Probability* review precedes it.

Statistics lectures
:   G. Cowan's statistical data analysis course,
    <https://www.pp.rhul.ac.uk/~cowan/stat_course.html>, builds the
    profile-likelihood framework from first principles and is the natural
    companion to the asymptotic-formulae paper [@cowan2011].
