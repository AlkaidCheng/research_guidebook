---
title: SLD
summary: The SLAC Large Detector at the SLAC Linear Collider, 1992–1998, from its polarised beam and detector to the mini-DST files in which its data survive.
references:
  schael2006zpole: "S. Schael et al. (ALEPH, DELPHI, L3, OPAL and SLD Collaborations, LEP Electroweak Working Group, SLD Electroweak and Heavy Flavour Groups), *Precision electroweak measurements on the Z resonance*, Phys. Rept. **427** (2006) 257, [arXiv:hep-ex/0509008](https://arxiv.org/abs/hep-ex/0509008)."
  abe2000alr: "K. Abe et al. (SLD Collaboration), *High-precision measurement of the left-right Z boson cross-section asymmetry*, Phys. Rev. Lett. **84** (2000) 5945, [arXiv:hep-ex/0004026](https://arxiv.org/abs/hep-ex/0004026)."
  phinney2000slc: "N. Phinney, *SLC final performance and lessons*, eConf **C000821** (2000) MO102, SLAC-PUB-8556, [arXiv:physics/0010008](https://arxiv.org/abs/physics/0010008)."
  slac1980cdr: "SLAC, *SLAC Linear Collider Conceptual Design Report*, SLAC-R-229 (1980), [INSPIRE 154130](https://inspirehep.net/literature/154130)."
  abe1997vxd3: "K. Abe et al., *Design and performance of the SLD vertex detector: a 307 Mpixel tracking system*, Nucl. Instrum. Meth. A **400** (1997) 287, [doi:10.1016/S0168-9002(97)01011-5](https://doi.org/10.1016/S0168-9002(97)01011-5)."
  abe1993alr: "K. Abe et al. (SLD Collaboration), *First measurement of the left-right cross section asymmetry in Z boson production by e⁺e⁻ collisions*, Phys. Rev. Lett. **70** (1993) 2515, [doi:10.1103/PhysRevLett.70.2515](https://doi.org/10.1103/PhysRevLett.70.2515)."
  sldhistory: "SLD Collaboration, *History of SLAC's Linear Collider Program for Accelerator Physics and Particle Physics*, SLD web documentation, [www-sldnt.slac.stanford.edu/alr/slchistory.htm](https://www-sldnt.slac.stanford.edu/alr/slchistory.htm)."
  cheng2026aiready: "C. L. Cheng, S. Corrodi, T. J. Hobbs, A. S. Mete and B. Nachman, *An AI-ready, polarized electron–positron collision dataset*, Mach. Learn.: Sci. Technol. **7** (2026) 050602, [doi:10.1088/2632-2153/aea5d7](https://doi.org/10.1088/2632-2153/aea5d7)."
  zenodo: "C. L. Cheng, B. Nachman, A. S. Mete, T. Hobbs, S. Corrodi, A. Johnson, M. Breidenbach and S. Dong, *SLD reconstructed mini-DSTs from the 1996–1998 SLC runs and documentation corpus*, Zenodo (2026), concept record [doi:10.5281/zenodo.19925959](https://doi.org/10.5281/zenodo.19925959)."
  lo2026parnassus: "Y.-F. Lo, C. L. Cheng and B. Nachman, *Cross-detector transfer learning with Parnassus: from ALEPH to SLD*, [arXiv:2609.25061](https://arxiv.org/abs/2609.25061) (2026)."
  jazellereader: "C. L. Cheng, *jazelle_reader: a modern Python reader for SLD Jazelle files*, version 0.4.0 (2026), [github.com/HEP-KE/jazelle_reader](https://github.com/HEP-KE/jazelle_reader)."
---

SLD, the SLAC Large Detector, recorded electron–positron collisions at the Z pole at the
SLAC Linear Collider from 1992 to 1998. Its electron beam was polarised, with a helicity
chosen at random for every bunch, and its vertex detector was built of CCDs. With about
600,000 Z decays, far fewer than the LEP experiments recorded, it gave the determination of
the weak mixing angle with the smallest uncertainty of all Z-pole measurements, and
measured the asymmetry parameters of the b and c quarks directly
[@schael2006zpole; @abe2000alr].

Figure 4.1 places the experiment in time. The collider was designed in
1980 and built from 1983 to 1987 [@slac1980cdr; @phinney2000slc]. SLD replaced the Mark II
detector at the interaction point in 1991 and saw its first Z from a polarised beam on
2 May 1992 [@sldhistory]. The polarisation rose from 22% in 1992 [@abe1993alr] to between
73% and 77% from 1994 on [@schael2006zpole], the vertex detector VXD3 arrived in 1996 [@abe1997vxd3], and the last data
were taken on 5 June 1998 [@sldhistory].

![The SLC and SLD from design to the last data, with the physics runs and their mean electron polarisation, and the recovery of the data in 2025–2026: the reader, the Zenodo releases, the dataset paper and the paper on cross-detector transfer.](../figures/sld-timeline.svg)

The reconstructed 1996–1998 data survive as mini-DST files, which were recovered,
validated and released in 2025–2026 together with simulated events and a reader that
converts them to modern formats [@cheng2026aiready; @zenodo; @jazellereader; @lo2026parnassus].
This chapter is the background to those files. It follows the data from the accelerator
to the bytes:

- [the SLC and its polarised beam](slc.md), with the polarimeter and the beam energy;
- [the physics of the Z pole](physics.md) with a polarised beam;
- [the detector](detector.md), subsystem by subsystem;
- [simulation and processing](simulation.md), from the generator to the mini-DST;
- [the mini-DST format](minidst.md): records, families, ids and numbers;
- the banks, field by field: [reconstruction](banks-reconstruction.md) and
  [event, beam and truth](banks-event-truth.md);
- [how the undocumented banks were decoded](decoding.md);
- [simulated events and the background overlay](mc-records.md);
- [the measurements and the data products](measurements.md).

!!! summary "Key points"
    - SLD ran at the SLC from 1992 to 1998 with a longitudinally polarised electron beam,
      recording about 600,000 Z decays.
    - The 1996–1998 reconstructed data survive as mini-DSTs, recovered and released in
      2026.
    - The following sections describe the accelerator, the physics, the detector, the
      simulation and the format of those files.
