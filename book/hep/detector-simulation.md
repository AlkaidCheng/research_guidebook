---
title: Detector Simulation
summary: Turning a generator-level event into the objects an experiment would reconstruct, with parametrised fast simulation and the questions to ask of any detector model.
references:
  delphes: "J. de Favereau et al., *DELPHES 3: a modular framework for fast simulation of a generic collider experiment*, JHEP **02** (2014) 057, [arXiv:1307.6346](https://arxiv.org/abs/1307.6346)."
  geant4: "S. Agostinelli et al., *Geant4: a simulation toolkit*, Nucl. Instrum. Meth. A **506** (2003) 250."
  geant4b: "J. Allison et al., *Recent developments in Geant4*, Nucl. Instrum. Meth. A **835** (2016) 186."
  atlfast3: "ATLAS Collaboration, *AtlFast3: the next generation of fast simulation in ATLAS*, Comput. Softw. Big Sci. **6** (2022) 7, [arXiv:2109.02551](https://arxiv.org/abs/2109.02551)."
  cmspf: "CMS Collaboration, *Particle-flow reconstruction and global event description with the CMS detector*, JINST **12** (2017) P10003, [arXiv:1706.04965](https://arxiv.org/abs/1706.04965)."
  fastjet: "M. Cacciari, G. P. Salam and G. Soyez, *FastJet user manual*, Eur. Phys. J. C **72** (2012) 1896, [arXiv:1111.6097](https://arxiv.org/abs/1111.6097)."
  antikt: "M. Cacciari, G. P. Salam and G. Soyez, *The anti-$k_t$ jet clustering algorithm*, JHEP **04** (2008) 063, [arXiv:0802.1189](https://arxiv.org/abs/0802.1189)."
  root: "R. Brun and F. Rademakers, *ROOT: an object oriented data analysis framework*, Nucl. Instrum. Meth. A **389** (1997) 81."
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
calorimeter showers. The experiments therefore maintain their own fast
simulations, in which the calorimeter showers are replaced by parametrisations
or generative models while the rest of the chain is unchanged [@atlfast3].

A **parametrised simulation** such as Delphes [@delphes] goes one step further
and replaces the material, the electronics and the reconstruction together
with parametrisations applied directly to the stable particles: efficiency
functions, resolution functions, and simple geometric acceptance. It runs in
milliseconds per event and is accurate to the extent that the parametrisations
were derived from a full simulation or from data. It cannot represent effects
that arise from the material itself: photon conversions, hadronic interactions
in the tracker, punch-through, pile-up at the hit level, or the correlations
between objects that share detector elements. Its value is in phenomenology,
in design studies, and in producing large labelled datasets whose detector
model is simple enough to state in a page.

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
  set EfficiencyFormula {
    (pt <= 0.1)                                          * (0.00) +
    (abs(eta) <= 1.5)                   * (pt > 0.1 && pt <= 1.0) * (0.70) +
    (abs(eta) <= 1.5)                   * (pt > 1.0)              * (0.95) +
    (abs(eta) > 1.5 && abs(eta) <= 2.5) * (pt > 0.1 && pt <= 1.0) * (0.60) +
    (abs(eta) > 1.5 && abs(eta) <= 2.5) * (pt > 1.0)              * (0.85) +
    (abs(eta) > 2.5)                                     * (0.00) }
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

The resolution and smearing modules (`MomentumSmearing`, the calorimeters'
`ResolutionFormula`) follow the same pattern: a formula in `pt`, `eta` and
`energy` giving the absolute or relative resolution, applied as a Gaussian.
The module reference in the Delphes documentation lists every class; the card
is only as good as the formulae in it.

## The Delphes pipeline

The excerpt above is a skeleton. The full CMS-like card runs thirty-odd
modules, and Figure 2.1 shows how they are connected. The structure is the
same in every shipped card: particles are propagated, the charged ones become
tracks, all of them deposit energy in calorimeter towers, tracks and towers
are combined into particle-flow candidates, and physics objects are built
from those candidates. The sections below follow the data through the card;
Table 2.1 lists the module classes involved.

![The dataflow of the CMS-like Delphes card. Boxes are modules, labelled with their class when it differs from their name; arrows are the named arrays that connect them. The two lanes in the middle are the tracking and calorimeter paths, which the particle-flow merger joins before any physics object is built.](figures/delphes-dataflow.svg)

| Class | Role | Defining parameters |
|---|---|---|
| `ParticlePropagator` | Propagate stable particles to the tracker surface; drop those born outside it | `Radius`, `HalfLength`, `Bz` |
| `Efficiency` | Keep each candidate with a probability | `EfficiencyFormula` |
| `MomentumSmearing` | Smear track momentum with a relative resolution | `ResolutionFormula` |
| `SimpleCalorimeter` | Sum energy into towers, smear it, split off particle-flow candidates | `EtaPhiBins`, `EnergyFraction`, `ResolutionFormula`, `EnergyMin` |
| `Merger` | Concatenate arrays, or sum them into a momentum | `InputArray` (several) |
| `PdgCodeFilter` | Keep or remove listed particle ids | `PdgCode`, `Invert`, `PTMin` |
| `Isolation` | Reject candidates with too much nearby activity | `DeltaRMax`, `PTMin`, `PTRatioMax` |
| `FastJetFinder` | Cluster jets with FastJet | `JetAlgorithm`, `ParameterR`, `JetPTMin` |
| `EnergyScale` | Rescale jet momenta | `ScaleFormula` |
| `JetFlavorAssociation` | Label jets by the partons near them | `DeltaR`, `PartonPTMin`, `PartonEtaMax` |
| `BTagging`, `TauTagging` | Set a tag bit with a flavour-dependent probability | `EfficiencyFormula` per flavour |
| `UniqueObjectFinder` | Remove objects that appear in more than one collection | input arrays in priority order |
| `TreeWriter` | Write arrays to the ROOT tree | `Branch` entries |

Table: The module classes of a standard Delphes card. Each is instantiated
once or several times under its own name in `ExecutionPath`.

### Propagation

`ParticlePropagator` reads `Delphes/stableParticles`, the status 1 particles
of the generator record, and moves each one to the surface of a cylinder
representing the tracker: charged particles along a helix in the solenoid
field, neutral ones in a straight line. Its outputs are the propagated
particles and, split off by type, the charged hadrons, electrons and muons
that the tracking modules will see. A particle whose production vertex lies
outside the propagation volume, by default the cylinder itself, is skipped,
so the daughters of a hadron that decayed beyond `Radius` or `HalfLength`
never enter the simulation. A charged particle whose helix curls up inside the
tracker never reaches the calorimeter surface, and the module records that
too. These two rules are where the generator's choice of stable particles
(Section 1.4.3) becomes a detector effect.

### Tracking

The charged outputs pass through one `Efficiency` and one `MomentumSmearing`
module per species. The efficiency is a function of `pt` and `eta`; in the
CMS-like card charged hadrons are found with probability 0.70 below 1 GeV and
0.95 above it in the barrel, somewhat less in the endcaps, and never beyond
$|\eta| = 2.5$ or below 0.1 GeV. The smearing applies a relative momentum
resolution of the form $\sqrt{a^2 + (b\,p_\mathrm{T})^2}$, a constant term
from multiple scattering and a term growing with momentum from the position
resolution, with coefficients per $|\eta|$ band. A `Merger` named
`TrackMerger` then concatenates the three species into the `tracks` array.
Each track carries the impact parameters `D0` and `DZ`, derived from the
propagated helix and the production vertex, which is why displaced decays
show up in Delphes output even though no secondary vertex is reconstructed.
Newer cards replace `MomentumSmearing` with `TrackSmearing`, which smears the
full set of helix parameters and writes their covariance.

### Calorimeters

The electromagnetic and hadronic calorimeters are two `SimpleCalorimeter`
modules, `ECal` and `HCal`, each with its own tower grid, energy sharing and
resolution.

- **Granularity.** `EtaPhiBins` entries define the tower edges: a list of
  $\eta$ boundaries, each with the number of $\phi$ divisions in that band.
  The CMS-like card uses $0.0174 \times 0.0174$ towers in the barrel and
  endcaps and much coarser ones in the forward region.
- **Energy sharing.** `EnergyFraction` gives, per particle id, the fraction
  of a particle's energy deposited in this calorimeter: in `ECal`, 1.0 for
  electrons, photons and $\pi^0$, 0.0 for other hadrons, muons and neutrinos,
  and 0.3 for $K^0_\mathrm{S}$ and $\Lambda$, with the complementary fractions
  in `HCal`. A new long-lived particle must be added to both lists or it
  deposits nothing.
- **Resolution.** `ResolutionFormula` is the absolute energy resolution,
  conventionally $\sigma(E) = \sqrt{(aE)^2 + b^2 E + c^2}$ with constant,
  stochastic and noise terms, evaluated per tower on the summed energy and
  applied as a Gaussian. `EnergyMin` and `EnergySignificanceMin` suppress
  towers below a threshold.
- **Particle flow.** Each calorimeter also receives the tracks. For every
  tower it compares the deposited energy with the momentum of the tracks
  pointing at it [@cmspf]: the track momenta are written out as
  `eflowTracks`, and the excess, if significant, becomes a neutral candidate,
  `eflowPhotons` from `ECal` and `eflowNeutralHadrons` from `HCal`. `HCal`
  takes its tracks from `ECal/eflowTracks`, so the two modules form a chain.

A `Merger` named `Calorimeter` concatenates the two tower arrays, and
`EFlowMerger` concatenates the tracks, photons and neutral hadrons into
`eflow`, the list of particle-flow candidates from which everything
downstream is built.

### Leptons and photons

Photon candidates are the `eflowPhotons`, electrons the tracks with
$|\mathrm{PID}| = 11$ selected by a `PdgCodeFilter`, and muons the smeared muon
tracks; muons deposit nothing in the calorimeters of this model. Each goes
through an `Efficiency` module, with thresholds such as $p_\mathrm{T} >
10$ GeV for leptons, and then an `Isolation` module. Isolation sums the
transverse momenta of the particle-flow candidates within `DeltaRMax` of the
candidate, excluding the candidate itself and anything below `PTMin`, and
keeps the candidate if the sum divided by its own $p_\mathrm{T}$ is below
`PTRatioMax`; the ratio is stored as `IsolationVar`. `EFlowFilter` removes
electrons and muons from the isolation input so that a lepton is not counted
against itself.

### Jets, tagging and missing momentum

`FastJetFinder` clusters the `eflow` candidates with anti-$k_t$ at
$R = 0.5$ and keeps jets above 20 GeV; a second instance, `GenJetFinder`,
clusters the generator-level stable particles with the neutrinos removed by
`NeutrinoFilter`, giving the `GenJet` collection against which the
reconstructed jets are calibrated. `JetEnergyScale` applies a
$p_\mathrm{T}$- and $\eta$-dependent correction. `JetFlavorAssociation`
labels each jet with the flavour of the partons within `DeltaR` of its axis,
in both the "physics" and "algorithmic" definitions, and `BTagging` and
`TauTagging` then set tag bits with a probability that depends on that
flavour: in the CMS-like card a $b$ jet is tagged with probability
$0.85\tanh(0.0025\,p_\mathrm{T})\cdot 25/(1 + 0.063\,p_\mathrm{T})$, a $c$
jet with a lower curve, and a light jet with about one percent. Several
taggers can set different bits of the same `BTag` word through `BitNumber`.
Missing transverse momentum is the negative vector sum of all `eflow`
candidates, computed by a `Merger` with a momentum output, and `ScalarHT` is
their scalar sum.

!!! remark "The order of UniqueObjectFinder is a physics choice"
    A photon, an electron and a jet can all be built from the same
    calorimeter deposit. `UniqueObjectFinder` takes its input arrays in
    priority order, photons then electrons then muons then jets in the
    shipped cards, and removes from each later collection any object that
    overlaps one already kept. The collections written to the tree are these
    de-duplicated ones. A card that reorders the inputs, or omits the module,
    changes which objects an analysis sees, and `GenJet`, which is not
    filtered, still contains the leptons.

## Reading the output

Delphes writes one ROOT [@root] file holding a tree named `Delphes`. Each
`add Branch` line of `TreeWriter` becomes a branch that stores an array of
objects of the named class, so the event is a set of parallel collections.
The CMS-like card writes the branches in Table 2.2.

| Branch | Class | Contents |
|---|---|---|
| `Event` | `HepMCEvent` | Weight, cross section, process id, scale, couplings, PDF information |
| `Particle` | `GenParticle` | The full generator record: `PID`, `Status`, mother and daughter indices, kinematics, charge, mass, production vertex |
| `Track`, `Tower` | `Track`, `Tower` | Reconstructed tracks and calorimeter towers |
| `EFlowTrack`, `EFlowPhoton`, `EFlowNeutralHadron` | `Track`, `Tower` | The particle-flow candidates |
| `Jet`, `FatJet`, `GenJet` | `Jet` | Reconstructed, large-radius and generator-level jets |
| `Electron`, `Muon`, `Photon` | `Electron`, `Muon`, `Photon` | Isolated leptons and photons after overlap removal |
| `MissingET`, `GenMissingET` | `MissingET` | Missing transverse momentum, reconstructed and generator-level |
| `ScalarHT` | `ScalarHT` | Scalar sum of transverse momenta |

Table: The branches written by the CMS-like card. Other cards add or omit
collections; the card is the authoritative list.

The `Particle` branch is the generator record as Delphes received it: `PID`
and `Status` are the generator's, the mother and daughter fields `M1`, `M2`,
`D1`, `D2` are indices into the same branch (−1 when absent), momenta are in
GeV, and the production vertex `X`, `Y`, `Z` is in mm with `T` in the same
units. Status 1 particles are the ones that were propagated; everything else
is history, available for truth labels.

Reconstructed objects keep links back to that history. `Track.Particle`,
`Electron.Particle` and `Muon.Particle` are references to the generator
particle the object was made from; `Jet.Constituents` lists the particle-flow
candidates that were clustered and `Jet.Particles` the generator particles
behind them. These links are ROOT object references, resolved inside ROOT by
the object's unique identifier. From Python, uproot reads the same arrays but
exposes a reference as the identifier it points at, which has to be matched
against the identifiers of the target branch; for most purposes it is simpler
to recompute the association from kinematics, for example by clustering the
`Particle` branch again or by $\Delta R$ matching.

!!! warning "Collections that describe the same energy"
    `Tower` and the three `EFlow` branches are two descriptions of the same
    calorimeter deposits, and `Track` overlaps `EFlowTrack`. Summing across
    them double counts. An analysis should pick one layer, the particle-flow
    candidates for anything jet-like, and the de-duplicated `Jet`,
    `Electron`, `Muon` and `Photon` collections for physics objects. `GenJet`
    is built from all stable particles but neutrinos, so in events with
    leptons it contains jets that `Jet` deliberately does not.

!!! recipe "A flat record with uproot"
    The fragment reads the jet collection and the event weight into
    jagged arrays and writes the jets above 30 GeV to Parquet, one row per
    event with a list of jets, which downstream tools read without ROOT.

    ```python
    import awkward as ak
    import uproot

    tree = uproot.open("delphes_output.root")["Delphes"]
    jets = tree.arrays(
        ["Jet.PT", "Jet.Eta", "Jet.Phi", "Jet.Mass", "Jet.Flavor", "Jet.BTag"],
        library="ak",
    )
    weight = tree["Event/Event.Weight"].array(library="ak")

    keep = jets["Jet.PT"] > 30.0
    record = ak.zip(
        {
            "weight": ak.firsts(weight),
            "jets": ak.zip(
                {
                    "pt": jets["Jet.PT"][keep],
                    "eta": jets["Jet.Eta"][keep],
                    "phi": jets["Jet.Phi"][keep],
                    "mass": jets["Jet.Mass"][keep],
                    "flavor": jets["Jet.Flavor"][keep],
                    "btag": jets["Jet.BTag"][keep],
                }
            ),
        },
        depth_limit=1,
    )
    ak.to_parquet(record, "jets.parquet")
    ```

    Branch names follow the pattern `<Branch>.<Field>`; `Event` holds one
    entry per event, hence `ak.firsts`. Read the `Particle` branch the same
    way when truth labels are needed, and store the Delphes version and the
    card beside the output.

## Validating a detector model

A card is a claim about a detector, and the claim is checked by comparing its
output with a reference: an official sample produced with the same card, a
published performance plot, or a full simulation of the same process. The
comparison is only meaningful if the generator-level input is the same, so
the first step is always to reproduce the generator configuration of the
reference, including the stability convention of Section 1.4.3, before any
detector-level quantity is looked at.

The observables worth comparing, in the order in which disagreements are
easiest to interpret:

1. **Generator level.** The `Particle` branch itself: multiplicities of
   status 1 particles, their $p_\mathrm{T}$ and $\eta$ spectra, and the
   fraction with displaced production vertices. A difference here is a
   generator difference and must be fixed first.
2. **Tracks.** Multiplicity, $p_\mathrm{T}$ spectrum and the `D0` and `DZ`
   distributions, whose tails come from $K^0_\mathrm{S}$, $\Lambda$ and
   heavy-flavour decays and are the most sensitive test of the propagation
   and stability conventions.
3. **Jets.** The response $p_\mathrm{T}^{\mathrm{reco}} / p_\mathrm{T}^{\mathrm{gen}}$
   against $p_\mathrm{T}$ and $\eta$ from matched `Jet`–`GenJet` pairs, the
   jet mass, and the numbers of charged and neutral constituents.
4. **Tagging and leptons.** Tagging efficiency against $p_\mathrm{T}$ per
   flavour, and lepton efficiency and isolation distributions.
5. **Event level.** Missing transverse momentum resolution and `ScalarHT`.

A parametrised simulation reproduces mean responses and the cores of
resolution distributions by construction, because those are the quantities
its formulae were fitted to. It does not reproduce tails that come from the
material, correlations between objects, or any quantity its formulae do not
mention. Agreement at the few-percent level in the quantities above is what
to expect from the same card; disagreement at that level in a tail is not a
bug, and disagreement in a mean is.

!!! recipe "Reproducing a reference sample"
    1. Obtain the reference's generator cards, Pythia settings and Delphes
       card, and the versions of all three programs. Where a version is
       unknown, infer it from the output: branches and fields differ between
       Delphes releases.
    2. Generate a small sample, a few thousand events, with the same seeds
       recorded.
    3. Compare the `Particle` branch first; proceed to tracks, jets, tags and
       event-level quantities only once it agrees.
    4. Plot each comparison as a ratio with statistical uncertainties, and
       record the plots next to the configuration.
    5. Only then scale up the production.

!!! warning "Pin the release with the card"
    The output tree depends on the Delphes release as much as on the card: a
    newer release adds fields, such as track masses and covariances, and
    changes the behaviour of some modules. A card from one release run under
    another produces a different file. Record the release and the card
    together, and treat a change in either as a new detector model.

!!! summary "Key points"
    - Full simulation transports particles through material with Geant4; a
      parametrised simulation such as Delphes applies efficiency and
      resolution functions to stable particles and runs a thousand times
      faster, at the price of everything the material does.
    - The Delphes card is the detector model: `ExecutionPath` orders the
      modules, and each module's formulae are the assumptions.
    - Propagation decides which generator particles exist for the detector;
      tracking and calorimetry smear them; particle flow joins the two; jets,
      leptons, tags and missing momentum are built from the candidates.
    - The output tree is a set of parallel collections with references back
      to the generator record. Pick one layer; do not sum overlapping ones.
    - Validate against a reference from the generator level outward, and pin
      the Delphes release together with the card.

## Further reading

Delphes
:   Project page at <https://delphes.github.io/> and source at
    <https://github.com/delphes/delphes>. The
    [WorkBook](https://delphes.github.io/workbook) covers installation,
    running and reading the output; its
    [modules](https://delphes.github.io/workbook/modules) page documents
    every module class and parameter, its
    [data-flow diagram](https://delphes.github.io/workbook/data-flow-diagram)
    is the full version of Figure 2.1, and its
    [tree description](https://delphes.github.io/workbook/root-tree-description)
    lists every field of every output class. The
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

ROOT and uproot
:   <https://root.cern/>. Delphes output is a ROOT tree; the *TFormula*
    documentation defines the expression syntax used in Delphes efficiency
    and resolution formulae. uproot (<https://uproot.readthedocs.io/>) and
    awkward (<https://awkward-array.org/>) read the trees from Python
    without ROOT.
