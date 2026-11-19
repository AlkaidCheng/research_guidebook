---
title: Simulated events and the background overlay
summary: What an MC record holds beyond a data record, how the random-trigger overlay shapes it, and what that means for identifying events and splitting samples.
references:
  johnson1994mcfarm: "T. Johnson, *The SLD MC Farm*, SLD web documentation (May 1994), [web.archive.org copy](https://web.archive.org/web/19990220144228/http://slacvx.slac.stanford.edu:80/sldmcwww/mc/farm.html)."
  abe1996rb: "K. Abe et al. (SLD Collaboration), *Measurements of $R_b$ with impact parameters and displaced vertices*, Phys. Rev. D **53** (1996) 1023, [doi:10.1103/PhysRevD.53.1023](https://doi.org/10.1103/PhysRevD.53.1023)."
  issue50: "jazelle_reader issue 50, *Which MCPART, PHKLUS and PHKMC1 entries does the mini-DST compressor drop?* (2026), [github.com/HEP-KE/jazelle_reader/issues/50](https://github.com/HEP-KE/jazelle_reader/issues/50)."
  jazellereader: "C. L. Cheng, *jazelle_reader: a modern Python reader for SLD Jazelle files*, version 0.4.0 (2026), [github.com/HEP-KE/jazelle_reader](https://github.com/HEP-KE/jazelle_reader)."
  banklab: "C. L. Cheng, *bank_lab: census, profiling and specification tools for the SLD mini-DST*, jazelle_reader development branch, unreleased (2026)."
  junk1995compress: "T. Junk, *The Compressed MiniDST*, SLD web documentation (December 1995), [web.archive.org copy](https://web.archive.org/web/20000417071834/http://www-sld.slac.stanford.edu:80/sldwww/compress.html)."
  sklearn: "F. Pedregosa et al., *Scikit-learn: machine learning in Python*, J. Mach. Learn. Res. **12** (2011) 2825, [arXiv:1201.0490](https://arxiv.org/abs/1201.0490)."
---

An SLD Monte Carlo record has the format of a data record, with five more families that
carry the truth of the simulation. It is also not a purely simulated event. The detector
noise and the beam-related background in it come from a real event, recorded at a random
beam crossing and merged with the simulated Z decay before reconstruction. Both facts
change how MC records must be used.

## The truth families

Five families appear only in MC records, and MCHEAD, present in every record, is filled
only in them.

- **MCHEAD** holds the number of final-state particles of the generated event and the
  generated interaction point.
- **MCPART** lists generated particles: the beams' products, the partons, the hadrons and
  their decay products, and the secondaries the detector simulation created. Each entry
  holds its momentum, a particle code, an origin word, the point where the particle ended
  and, packed into one word, its own id, its parent's id and its charge. No document
  defines the particle codes; the masses of two-body decays show that they match the
  numbering of JETSET 6 (1 photon, 7 electron, 9 muon, 17 charged pion, 18 charged kaon,
  23 neutral pion, 41 proton, 42 neutron) [@banklab].
- **MCBEAM** holds the generated beams: their energies and four-momenta, the generated
  interaction point and the beam helicity, ±1. The simulation generates fully polarised
  beams with each helicity in half of the events, so the samples can be reweighted to any
  polarisation.
- **MCPNT** relates generated particles to reconstructed particles (PHPOINT), with the
  number of hits and the energy each particle contributed; **PHKMC1** relates them to
  calorimeter clusters, with the energy deposited and the point where the particle reached
  the calorimeter; **PHWMC** attributes the hits of a muon-system track to particles.
- Two reconstructed families point back to the truth: a track's `imc` field names its
  generated particle, and each VXD3 hit names the particle that made it.

The mini-DST keeps only part of the full simulation record. About a fifth of the MCPART
ids survive, always with the first block of ids, which holds the primary quarks and the
generator history, and always with the ancestors of every kept particle; the ids keep
their numbering in the full record, so they have gaps [@issue50]. Every kept PHKMC1
relation points to a kept particle [@issue50], so the relations of a dropped particle were
removed with it; the memo on the compressed format notes that Jazelle sometimes deletes
the banks that point to a deleted MCPART [@junk1995compress]. PHWMC, in contrast, still
refers to some particles the mini-DST did not keep [@banklab]. The truth record is
therefore not the full generator history, and which particles the compressor kept, and
why, is not documented [@issue50].

## The random-trigger overlay

Rather than simulate the beam-related background, the readout noise and the dead
channels, SLD took them from data. Simulated Z decays were overlaid with the detector
signals of events recorded on random beam crossings close in time to real Z decays, which
also supplied the dead channels and the high-voltage status of the drift chamber, so the
simulation followed the time dependence of the beam conditions [@abe1996rb]. The MC
production farm chose the *random-trigger* events by running period and computed how often
each had to be reused to reach the requested number of simulated events
[@johnson1994mcfarm]. Each random-trigger event therefore served several simulated
events.

!!! definition "Random-trigger event"
    A detector readout taken at a beam crossing chosen at random, independent of any
    collision. It records what the detector sees without a physics event: its status, its
    noise and the beam-related background at that moment.

The merge leaves a clear trace in the mini-DST (Figure 4.40)
[@issue50; @banklab]:

- the **header label** of an MC record, the run and event numbers in IEVENTH, is that of
  its random-trigger event, so several MC records share one label;
- the **detector-status words** of PHEVCL describe the real detector at the moment of the
  random trigger: the VXD3 word, which goes with dead sectors, the CDC bits 0 to 14 and
  the CRID word are the same in all records that share the label, and only the CDC veto
  bit 15 varies from record to record;
- **background calorimeter clusters**, which no simulated particle touched, mostly
  reappear byte for byte in other records that share the label;
- the **truth families, PHBM and MCBEAM** are simulated and differ from record to record;
  so do the tracks, which almost never come out identical.

![The random-trigger overlay. One recorded random-trigger event is merged with several simulated Z decays. Its label, its detector-status words (all but one bit) and its detector signals go into each MC record that uses it, and most of its background clusters reappear there byte for byte; the truth, the beam values and everything the simulated particles touched are different in every record.](../figures/sld-overlay.svg)

## Consequences for analysis

Three rules follow.

1. **An MC event is identified by its position, never by its label.** In MC, (run, event)
   names the random-trigger event, not the simulated decay. Joining or deduplicating MC
   records on it merges different events.
2. **Unlinked clusters are mostly background.** A calorimeter cluster without a PHKMC1
   relation is, in most cases, a cluster of the overlaid event, and not a simulated
   particle whose relation was lost. Among unlinked clusters, 93% of those below 0.02 GeV
   and about 70% of those above 0.2 GeV have a byte-identical copy in another record with
   the same label, against at most 1.5% of linked clusters [@issue50].
3. **Samples must be split by label group.** Records that share a label share their
   background, so a split by record puts the same background clusters into a training and
   a test sample.

!!! recipe "Splitting MC records by overlay label"
    ```python
    import jazelle
    import numpy as np
    from sklearn.model_selection import GroupShuffleSplit

    run, event = [], []
    for path in mc_paths:                     # all MC files of the sample together
        with jazelle.open(path) as f:
            for i in range(len(f)):
                header = f[i].ieventh
                run.append(header.run)
                event.append(header.event)

    labels = np.stack([run, event], axis=1)
    _, group = np.unique(labels, axis=0, return_inverse=True)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=0)
    train, test = next(splitter.split(labels, groups=group))
    ```
    The group of a record is its label over the whole sample, since a label can recur in
    more than one file. `GroupShuffleSplit` [@sklearn] keeps every group on one side of
    the split.

!!! warning "Reader errors that affect MC"
    In jazelle 0.4.0 [@jazellereader] and earlier the MC PHBM values are read from the
    wrong bytes, and the MCPART charges and rebuilt energies are wrong [@banklab]. The
    development branch corrects only the charges: it still reads MC PHBM from the wrong
    bytes, does not decode MCBEAM and rebuilds the energies with the same wrong masses
    [@banklab]. Until the
    decoders exist, read the beam values from the MCBEAM bytes with the layout given in
    [the section on the truth banks](banks-event-truth.md), and recompute each omitted
    energy from the momentum and the JETSET 6 mass of the particle code.

!!! summary "Key points"
    - MC records add five truth families to the data format and fill MCHEAD.
    - Each MC record merges a simulated Z decay with a recorded random-trigger event, and
      takes its label and detector status from that event.
    - Most background clusters recur byte for byte in other records that share a label;
      truth, beam values and tracks do not.
    - Identify MC events by position, treat unlinked clusters as background, and split
      samples by label group.

## Further reading

The MC farm documentation [@johnson1994mcfarm] describes how the production jobs used
the random-trigger files, and issue 50 of the reader [@issue50] records the tests behind
the statements on background clusters and on the entries the compressor kept.
