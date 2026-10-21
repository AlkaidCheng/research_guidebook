---
title: Detector Simulation
summary: Turning a generator-level event into the objects an experiment would reconstruct, with parametrised fast simulation and the questions to ask of any detector model.
status: in-preparation
references:
  delphes: "J. de Favereau et al., *DELPHES 3: a modular framework for fast simulation of a generic collider experiment*, JHEP **02** (2014) 057, [arXiv:1307.6346](https://arxiv.org/abs/1307.6346)."
  geant4: "S. Agostinelli et al., *Geant4: a simulation toolkit*, Nucl. Instrum. Meth. A **506** (2003) 250."
  geant4b: "J. Allison et al., *Recent developments in Geant4*, Nucl. Instrum. Meth. A **835** (2016) 186."
  fastjet: "M. Cacciari, G. P. Salam and G. Soyez, *FastJet user manual*, Eur. Phys. J. C **72** (2012) 1896, [arXiv:1111.6097](https://arxiv.org/abs/1111.6097)."
  antikt: "M. Cacciari, G. P. Salam and G. Soyez, *The anti-$k_t$ jet clustering algorithm*, JHEP **04** (2008) 063, [arXiv:0802.1189](https://arxiv.org/abs/0802.1189)."
---

## Fast and full simulation

A **full simulation** tracks every generator-level particle through a detailed
model of the detector with Geant4 [@geant4; @geant4b]. The detector is a
hierarchy of volumes with assigned materials; a *physics list* selects the
models for electromagnetic showers, hadronic interactions, multiple scattering
and decays in flight; and each particle is transported step by step, producing
secondaries and depositing energy. A *digitisation* step then converts the
deposits into the signals the electronics would record, and the experiment's
own reconstruction runs on those signals exactly as it does on data. Full
simulation is the most faithful description available, and the most
expensive: minutes of CPU per event for an LHC detector, dominated by
calorimeter showers.

A **fast simulation** such as Delphes [@delphes] replaces the material and the
electronics with parametrisations applied directly to the stable particles:
efficiency functions, resolution functions, and simple geometric acceptance.
It runs in milliseconds per event and is accurate to the extent that the
parametrisations were derived from a full simulation or from data. It cannot
represent effects that arise from the material itself: photon conversions,
hadronic interactions in the tracker, punch-through, pile-up at the hit level,
or the correlations between objects that share detector elements. Its value
is in phenomenology, in design studies, and in producing large labelled
datasets whose detector model is simple enough to state in a page.

## The Delphes card

A Delphes detector is a **card**, a Tcl script with two kinds of statement:
`set ExecutionPath { ... }` lists the modules in the order they run, and one
`module <Class> <Name> { ... }` block per module sets its parameters with
`set` and `add`. Modules communicate through named arrays
(`<Module>/<array>`), so the card is a dataflow graph as much as a parameter
file. The excerpt below is drawn from the CMS-like card shipped with Delphes;
comments mark the lines that define the detector model.

```text
set ExecutionPath {
  ParticlePropagator
  ChargedHadronTrackingEfficiency
  ChargedHadronMomentumSmearing
  Calorimeter
  EFlowMerger
  FastJetFinder
  BTagging
  TreeWriter
}

module ParticlePropagator ParticlePropagator {
  set InputArray Delphes/stableParticles     # generator-level stable particles
  set OutputArray stableParticles
  set ChargedHadronOutputArray chargedHadrons
  set ElectronOutputArray electrons
  set MuonOutputArray muons
  set Radius 1.29        # tracker radius in m: particles born outside are dropped
  set HalfLength 3.00    # tracker half-length in m
  set Bz 3.8             # solenoid field in T
}

module Efficiency ChargedHadronTrackingEfficiency {
  set InputArray ParticlePropagator/chargedHadrons
  set OutputArray chargedHadrons
  # efficiency as a function of pt (GeV) and eta; a product of step functions
  set EfficiencyFormula { (pt <= 0.1) * (0.00) +
                          (abs(eta) <= 1.5) * (pt > 0.1 && pt <= 1.0) * (0.70) +
                          (abs(eta) <= 1.5) * (pt > 1.0)              * (0.95) +
                          (abs(eta) > 1.5 && abs(eta) <= 2.5) * (pt > 0.1 && pt <= 1.0) * (0.60) +
                          (abs(eta) > 1.5 && abs(eta) <= 2.5) * (pt > 1.0)              * (0.85) +
                          (abs(eta) > 2.5) * (0.00) }
}

module FastJetFinder FastJetFinder {
  set InputArray EFlowMerger/eflow           # particle-flow candidates
  set OutputArray jets
  set JetAlgorithm 6     # 4 = kt, 5 = Cambridge/Aachen, 6 = anti-kt
  set ParameterR 0.5     # jet radius
  set JetPTMin 20.0      # minimum jet pt in GeV written out
}

module TreeWriter TreeWriter {
  add Branch Delphes/allParticles Particle GenParticle   # the full generator record
  add Branch FastJetFinder/jets Jet Jet                  # reconstructed jets
}
```

`ExecutionPath` is the pipeline; a module absent from it does not run even if
its block is present. `ParticlePropagator` is the first physics module and the
one that decides which generator-level particles the detector sees at all: it
propagates charged particles along helices in the field `Bz` and drops any
particle whose production vertex lies outside the cylinder of radius `Radius`
and half-length `HalfLength`, which is why the generator's stability
convention (Section 1.4.3) changes a Delphes sample. `Efficiency` modules
accept each particle with a probability given by `EfficiencyFormula`, a
function of `pt`, `eta`, `phi` and `energy` written in ROOT's formula syntax;
the product-of-step-functions form above is the conventional way of writing a
lookup table. `FastJetFinder` wraps FastJet [@fastjet]; algorithm 6 is
anti-$k_t$ [@antikt], and `ParameterR` and `JetPTMin` are the two numbers
most often changed between detector models. `TreeWriter` chooses what is
saved: each `add Branch` names an input array, the branch name and the output
class. Everything not written here is lost, and `Delphes/allParticles` is the
branch to keep when truth labels will be needed later.

The resolution and smearing modules (`MomentumSmearing`, the calorimeter's
`ResolutionFormula`) follow the same pattern: a formula in `pt`, `eta` and
`energy` giving the relative resolution, applied as a Gaussian. The module
reference in the Delphes distribution documents every class; the card is only
as good as the formulae in it.

## The Delphes pipeline

The section will walk the chain of the card above module by module:
propagation, tracking efficiency and momentum smearing, calorimeter towers
with their $\eta$–$\phi$ segmentation, particle-flow merging, isolation,
jet clustering, flavour tagging, and missing transverse momentum, with the
input and output arrays that connect them.

## Reading the output

The Delphes ROOT output holds one branch per `TreeWriter` entry: tracks,
towers, particle-flow candidates, jets, leptons and the generator-level
`Particle` branch. The section covers the relationships between them, the
pitfalls of mixing branches from different stages, and a disciplined way of
extracting a flat record for downstream analysis.

## Validating a detector model

A detector model is validated against a reference: an official sample, a
published performance plot or a full simulation. The section lists the
observables to compare (track multiplicity and impact-parameter distributions,
jet response and resolution, tagging efficiencies) and the level of agreement
to expect from a parametrised simulation.

## Further reading

Delphes
:   Project page at <https://cp3.irmp.ucl.ac.be/projects/delphes> and source
    at <https://github.com/delphes/delphes>. The
    [WorkBook](https://cp3.irmp.ucl.ac.be/projects/delphes/wiki/WorkBook) on
    the wiki covers installation, running, and reading the output; its
    [Modules](https://cp3.irmp.ucl.ac.be/projects/delphes/wiki/WorkBook/Modules)
    page documents every module class and parameter that a card can set. The
    [shipped cards](https://github.com/delphes/delphes/tree/master/cards) in
    the repository are the reference detector models and the starting point
    for any new one.

Geant4
:   <https://geant4.web.cern.ch/>, with the user guides at
    <https://geant4-userdoc.web.cern.ch/>. The
    [Book For Application Developers](https://geant4-userdoc.web.cern.ch/UsersGuides/ForApplicationDeveloper/html/index.html)
    explains geometry, materials and physics lists; the *Physics Reference
    Manual* documents the interaction models.

FastJet
:   <https://fastjet.fr/>. The manual [@fastjet] defines the clustering
    algorithms and the recombination schemes that Delphes exposes through
    `FastJetFinder`.

ROOT
:   <https://root.cern/>. Delphes output is a ROOT tree; the *TFormula*
    documentation defines the expression syntax used in Delphes efficiency
    and resolution formulae, and *uproot* (<https://uproot.readthedocs.io/>)
    reads the trees from Python without ROOT.
