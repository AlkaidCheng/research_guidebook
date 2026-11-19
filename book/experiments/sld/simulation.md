---
title: Simulation and processing
summary: How SLD simulated Z decays and its detector, merged recorded background into the simulation, and processed both simulated and recorded events into DSTs and mini-DSTs.
references:
  bower1995eventsim: "G. Bower, *Physics Event Simulation at SLD*, SLD web documentation (September 1995), [web.archive.org copy](https://web.archive.org/web/20000419081603/http://www-sld.slac.stanford.edu:80/sldwww/eventsim.html)."
  sjostrand1994jetset: "T. Sjöstrand, *High-energy-physics event generation with PYTHIA 5.7 and JETSET 7.4*, Comput. Phys. Commun. **82** (1994) 74, [doi:10.1016/0010-4655(94)90132-5](https://doi.org/10.1016/0010-4655(94)90132-5)."
  jadach1994koralz: "S. Jadach, B. F. L. Ward and Z. Wąs, *The Monte Carlo program KORALZ version 4.0 for lepton or quark pair production at LEP/SLC energies*, Comput. Phys. Commun. **79** (1994) 503, [doi:10.1016/0010-4655(94)90190-2](https://doi.org/10.1016/0010-4655(94)90190-2)."
  jadach1993tauola: "S. Jadach, Z. Wąs, R. Decker and J. H. Kühn, *The τ decay library TAUOLA, version 2.4*, Comput. Phys. Commun. **76** (1993) 361, [doi:10.1016/0010-4655(93)90061-G](https://doi.org/10.1016/0010-4655(93)90061-G)."
  brun1994geant: "R. Brun et al., *GEANT Detector Description and Simulation Tool*, CERN Program Library Long Writeup W5013 (1994), [doi:10.17181/CERN.MUHF.DMJ1](https://doi.org/10.17181/CERN.MUHF.DMJ1)."
  abe1996rb: "K. Abe et al. (SLD Collaboration), *Measurements of $R_b$ with impact parameters and displaced vertices*, Phys. Rev. D **53** (1996) 1023, [doi:10.1103/PhysRevD.53.1023](https://doi.org/10.1103/PhysRevD.53.1023)."
  abe2005rbrc: "K. Abe et al. (SLD Collaboration), *Measurement of the branching ratios of the Z⁰ into heavy quarks*, Phys. Rev. D **71** (2005) 112004, [arXiv:hep-ex/0503005](https://arxiv.org/abs/hep-ex/0503005)."
  abe2001lepton: "K. Abe et al. (SLD Collaboration), *Improved direct measurement of leptonic coupling asymmetries with polarized Z bosons*, Phys. Rev. Lett. **86** (2001) 1162, [arXiv:hep-ex/0010015](https://arxiv.org/abs/hep-ex/0010015)."
  johnson1994farm: "T. Johnson, *The SLD MC Farm*, SLD web documentation (May 1994), [web.archive.org copy](https://web.archive.org/web/19990220144228/http://slacvx.slac.stanford.edu:80/sldmcwww/mc/farm.html)."
  duboisp1p2: "R. Dubois, *Pass1 & Pass2 Processing of Data*, SLD web documentation, [web.archive.org copy](https://web.archive.org/web/20000419221751/http://www-sld.slac.stanford.edu:80/sldwww/p1p2.html)."
  dubois1994primer: "R. Dubois, *SLD Primer*, SLD web documentation (May 1994), [web.archive.org copy](https://web.archive.org/web/20000309140423/http://www-sld.slac.stanford.edu:80/sldwww/PRIMER/SLDPRIMER.HTML)."
  weiss1995processors: "E. Weiss, *Workbook for SLD Offline Users: IDA Processors*, SLD web documentation (January 1995), [web.archive.org copy](https://web.archive.org/web/19990220153900/http://www-sld.slac.stanford.edu:80/sldwww/workbook/PROCESSORS.HTML)."
  strauss1994mdst: "M. Strauss, *The SLD Mini-DST, Version 1.0*, SLD web documentation (March 1994), [web.archive.org copy](https://web.archive.org/web/20000119035549/http://www-sld.slac.stanford.edu:80/sldwww/mdst/mdst.html)."
  junk1995compress: "T. Junk, *The Compressed MiniDST*, SLD web documentation (December 1995), [web.archive.org copy](https://web.archive.org/web/20000417071834/http://www-sld.slac.stanford.edu:80/sldwww/compress.html)."
  johnson1990jazelle: "A. S. Johnson, *JAZELLE Users Manual*, SLAC-R-362 (1990), [INSPIRE 308646](https://inspirehep.net/literature/308646)."
  johnson1990chep: "A. S. Johnson, M. Breidenbach, H. Hissen, P. F. Kunz, D. J. Sherden and T. Burnett, *JAZELLE: an enhanced data management system for high energy physics*, AIP Conf. Proc. **209** (1990) 285, [doi:10.1063/1.39573](https://doi.org/10.1063/1.39573)."
  johnson1991mcpart: "T. Johnson and G. Word, *MCPART: Monte Carlo particle bank*, version 0.52, SLD DUCS bank template (April 1991), [web.archive.org copy](https://web.archive.org/web/20010906181156/http://www-sld.slac.stanford.edu:80/ducs/prod/mc/mcpart.template)."
  jazellereader: "C. L. Cheng, *jazelle_reader: a modern Python reader for SLD Jazelle files*, version 0.4.0 (2026), [github.com/HEP-KE/jazelle_reader](https://github.com/HEP-KE/jazelle_reader)."
---

A simulated SLD event passes through the same stages as a real one, and then through the
same reconstruction. This section follows an event from the generator to the mini-DST,
first for simulation, then for recorded data, and ends with the step that turned the
DSTs into the compact files that survive.

## From the collision to particles

SLD simulated an annihilation in three stages: the beam, the event, and the detector
response [@bower1995eventsim]. The beam simulation MCSLC drew the beam energies, the
electron polarisation and the interaction point, and wrote them to the bank MCBEAM, which
the generator then read. SLD ran all its offline jobs in IDA (Interactive Data Analysis),
in which the main simulation and reconstruction codes were processors, IDA routines that
returned their output as banks [@johnson1990chep; @weiss1995processors]. Every generator was such a processor, and its
standard output was one MCPART bank for every particle it created, not only the final ones,
and one MCHEAD bank for the event; a few older generators still wrote the earlier banks MCTRACK, MCROOTS and
MCEVENT.

Figure 4.11 shows the stages inside the generator, followed by the detector simulation and
the reconstruction. The hard process produces a quark and an antiquark from the Z; the
parton shower lets them radiate gluons, which branch further; the Lund string model turns
the coloured partons into hadrons; and short-lived hadrons decay [@sjostrand1994jetset].
Long-lived ones were left to the detector simulation, which decayed them in flight and
flagged them so in MCPART [@johnson1991mcpart]. In a scan of one 1996 MC file with jazelle
0.4.0, that flag marks hadrons such as $K^0_S$, $K^\pm$ and $\Lambda$, and the generator's
decay flag never does [@jazellereader]. The recommended generator
for hadronic events from 1995, MCL74, was JETSET 7.4 with an improved package of B-meson decays from the
CLEO collaboration; its predecessor, MCLUND, was JETSET 6.3 [@bower1995eventsim]. The
heavy-flavour analyses retuned the B decays to measurements at the Υ(4S)
[@abe2005rbrc]. τ pairs were generated with KORALZ 4.0 and the TAUOLA decay library
[@jadach1994koralz; @jadach1993tauola; @abe2001lepton].

![An e⁺e⁻ → Z → q q̄ event at its stages, stylised. The generator produces the hard process, the parton shower, the hadronisation and the decays of short-lived hadrons; the detector simulation propagates the particles through the detector and decays the long-lived ones, such as K⁰ₛ, K± and Λ, in flight; the reconstruction recovers tracks, clusters and particles, from which jets and event shapes are built.](../figures/sld-event-stages.svg)

## Simulating the detector

The detector simulation was GEANT 3, run inside IDA as the processor GSIM, with the
geometry, materials and tracking parameters of each subsystem loaded from SLD's constant
files [@bower1995eventsim; @brun1994geant]. Electromagnetic showers in the calorimeter
could be followed in full with the EGS program or replaced by a faster parametrisation. The
simulation wrote raw-data banks almost identical to those the online system wrote
[@bower1995eventsim], so the same reconstruction ran on both; only the calorimeter raw data
of recorded events had first to be converted by the processor KALKLU [@weiss1995processors]. Early analyses used GEANT 3.15 and the later
ones GEANT 3.21, with the simulated geometry smeared by the uncertainties left after
alignment [@abe1996rb; @abe2005rbrc].

The beam-related background, the detector noise and the dead channels were not simulated
but taken from data. Simulated Z decays were overlaid with the detector signals of events
recorded on random beam crossings close in time to real Z decays, which also supplied the
dead channels and the high-voltage status of the drift chamber
[@abe1996rb]. The Monte Carlo therefore followed the beam conditions and the detector state
of the data, weighted by luminosity. The production farm selected the random-trigger events
by running period and reused each of them for several simulated events
[@johnson1994farm]; [the section on MC records](mc-records.md) describes what this means
for the mini-DSTs.

## Reconstruction and recorded data

Figure 4.12 sets the two paths side by side. Recorded events
started as raw detector data. A first pass, PASS1, filtered the triggers and kept about
3% of them in 1993, recording its decisions as event-class bits; a second pass, PASS2,
reconstructed every physics event that survived and tagged Bhabha, hadronic, τ-pair and
muon-pair candidates [@duboisp1p2]. PASS2 was not meant for physics: analyses used later
reconstructions, with frozen production code, of all the events that passed the PASS1
physics filters [@dubois1994primer].

![The two processing paths. Simulated events: the beam simulation, the generator, the GEANT 3 detector simulation and the overlay of a recorded random-trigger event. Recorded events: the readout, the PASS1 filter and the PASS2 first reconstruction, which was not used for physics. The simulated events and the recorded events that passed the PASS1 physics filters are reconstructed by the same code into DSTs, from which the compressed mini-DSTs are written.](../figures/sld-processing-chains.svg)

The full reconstruction was one driving processor, RECSLD, which ran ten processors for
the tracking, its extrapolation, the CRID, the calorimeter, the muon system and the matching
between them, filled the physics banks, and for simulated events linked the reconstructed
objects to the MCPART truth [@weiss1995processors]. All SLD data, raw, reconstructed and
simulated, were Jazelle files [@dubois1994primer; @johnson1990jazelle].

## From DST to mini-DST

The full DSTs were too large to keep on the collaboration's VAX disks. The mini-DST,
defined in March 1994, was a lean version for physics analysis only, with targets of about
10 kB per data event and 20 kB per MC event, and new banks under new names in place of the
DST banks, PHCHRG alone replacing three tracking banks [@strauss1994mdst]. Jets and event
shapes were not stored; users computed them from the stored particles. A compressed
format, described in a memo of December 1995, stores all banks of an event in one packed
block and reads about five times faster [@junk1995compress]. It is the format of the
surviving files, which [the next section](minidst.md) describes.

!!! summary "Key points"
    - The beam simulation MCSLC wrote MCBEAM; generators (JETSET 7.4 as MCL74 for hadronic
      events, KORALZ with TAUOLA for τ pairs) wrote MCPART and MCHEAD.
    - GEANT 3, run as GSIM, simulated the detector and wrote raw-data banks.
    - Background, noise and dead channels came from recorded random-trigger events
      overlaid on the simulated ones.
    - Simulated and recorded events passed through the same reconstruction, RECSLD, into
      DSTs and then the compressed mini-DSTs.

## Further reading

The event-simulation guide [@bower1995eventsim] lists every generator SLD used, and the
$R_b$ paper of 1996 [@abe1996rb] describes the simulation and the overlay as used in physics.
