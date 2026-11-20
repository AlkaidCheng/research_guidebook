---
title: Measurements and data products
summary: SLD's published electroweak results, how the recovered data reproduce the key ones, and where to find the papers, data and software of the recovery.
references:
  abe1993alr: "K. Abe et al. (SLD Collaboration), *First measurement of the left-right cross section asymmetry in Z boson production by e⁺e⁻ collisions*, Phys. Rev. Lett. **70** (1993) 2515, [doi:10.1103/PhysRevLett.70.2515](https://doi.org/10.1103/PhysRevLett.70.2515)."
  abe1994alr: "K. Abe et al. (SLD Collaboration), *Precise measurement of the left-right cross section asymmetry in Z boson production by e⁺e⁻ collisions*, Phys. Rev. Lett. **73** (1994) 25, [arXiv:hep-ex/9404001](https://arxiv.org/abs/hep-ex/9404001)."
  abe1997alr: "K. Abe et al. (SLD Collaboration), *Improved measurement of the left-right Z⁰ cross section asymmetry*, Phys. Rev. Lett. **78** (1997) 2075, [arXiv:hep-ex/9611011](https://arxiv.org/abs/hep-ex/9611011)."
  abe2000alr: "K. Abe et al. (SLD Collaboration), *High-precision measurement of the left-right Z boson cross-section asymmetry*, Phys. Rev. Lett. **84** (2000) 5945, [arXiv:hep-ex/0004026](https://arxiv.org/abs/hep-ex/0004026)."
  abe2001lepton: "K. Abe et al. (SLD Collaboration), *Improved direct measurement of leptonic coupling asymmetries with polarized Z bosons*, Phys. Rev. Lett. **86** (2001) 1162, [arXiv:hep-ex/0010015](https://arxiv.org/abs/hep-ex/0010015)."
  abe2005rbrc: "K. Abe et al. (SLD Collaboration), *Measurement of the branching ratios of the Z⁰ into heavy quarks*, Phys. Rev. D **71** (2005) 112004, [arXiv:hep-ex/0503005](https://arxiv.org/abs/hep-ex/0503005)."
  abe2005abac: "K. Abe et al. (SLD Collaboration), *Direct measurements of $A_b$ and $A_c$ using vertex and kaon charge tags at the SLAC Detector*, Phys. Rev. Lett. **94** (2005) 091801, [arXiv:hep-ex/0410042](https://arxiv.org/abs/hep-ex/0410042)."
  schael2006zpole: "S. Schael et al. (ALEPH, DELPHI, L3, OPAL and SLD Collaborations, LEP Electroweak Working Group, SLD Electroweak and Heavy Flavour Groups), *Precision electroweak measurements on the Z resonance*, Phys. Rept. **427** (2006) 257, [arXiv:hep-ex/0509008](https://arxiv.org/abs/hep-ex/0509008)."
  erler2024pdg: "J. Erler and A. Freitas, *Electroweak model and constraints on new physics*, in S. Navas et al. (Particle Data Group), Phys. Rev. D **110** (2024) 030001, [doi:10.1103/PhysRevD.110.030001](https://doi.org/10.1103/PhysRevD.110.030001)."
  cheng2026aiready: "C. L. Cheng, S. Corrodi, T. J. Hobbs, A. S. Mete and B. Nachman, *An AI-ready, polarized electron–positron collision dataset*, Mach. Learn.: Sci. Technol. **7** (2026) 050602, [doi:10.1088/2632-2153/aea5d7](https://doi.org/10.1088/2632-2153/aea5d7)."
  lo2026parnassus: "Y.-F. Lo, C. L. Cheng and B. Nachman, *Cross-detector transfer learning with Parnassus: from ALEPH to SLD*, [arXiv:2609.25061](https://arxiv.org/abs/2609.25061) (2026)."
  zenodo: "C. L. Cheng, B. Nachman, A. S. Mete, T. Hobbs, S. Corrodi, A. Johnson, M. Breidenbach and S. Dong, *SLD reconstructed mini-DSTs from the 1996–1998 SLC runs and documentation corpus*, Zenodo (2026), concept record [doi:10.5281/zenodo.19925959](https://doi.org/10.5281/zenodo.19925959)."
  jazellereader: "C. L. Cheng, *jazelle_reader: a modern Python reader for SLD Jazelle files*, version 0.4.0 (2026), [github.com/HEP-KE/jazelle_reader](https://github.com/HEP-KE/jazelle_reader); PyPI package [jazelle](https://pypi.org/project/jazelle/)."
  sldresurrect: "HEP-KE, *sld-resurrect: modern reanalysis tooling for the SLAC Large Detector experiment*, version 0.2.0 (2026), [github.com/HEP-KE/sld-resurrect](https://github.com/HEP-KE/sld-resurrect)."
---

SLD's determination of the weak mixing angle is the most precise of the measurements at
the Z pole, and its heavy-flavour asymmetries enter every global fit of the electroweak
theory [@schael2006zpole]. This section collects the published results, shows how the recovered 1996–1998
data reproduce the central ones, and lists the papers, data records and software of the
recovery.

## The left-right asymmetry

Table 4.27 gives the left-right asymmetry of each running period. The
measurement grew with the polarisation of the source and with the luminosity, from about
ten thousand Z decays in 1992 to over three hundred thousand in 1997–98.

<!-- table:alr-periods -->
| Period | Z decays | $\langle \lvert P_e\rvert\rangle$ | $A_{LR}^0$ | Reference |
|---|---|---|---|---|
| 1992 | 10,224 | 22.4% | $0.100 \pm 0.044 \pm 0.004$ (at 91.55 GeV) | [@abe1993alr] |
| 1993 | 49,392 | 63.0% | $0.1656 \pm 0.0071 \pm 0.0028$ | [@abe1994alr] |
| 1994–95 | 93,644 | 77.2% | $0.1512 \pm 0.0042 \pm 0.0011$ | [@abe1997alr] |
| 1996 | 51,873 | 76.2% | $0.1593 \pm 0.0057 \pm 0.0010$ | [@abe2000alr] |
| 1997–98 | 331,614 | 72.9% | $0.1491 \pm 0.0024 \pm 0.0010$ | [@abe2000alr] |
| 1992–98 | 537,000 | | $0.15138 \pm 0.00216$ | [@abe2000alr] |

Table: SLD measurements of the left-right asymmetry at the Z pole, with statistical and systematic uncertainties, and the total uncertainty for the combined value. The 1992 value is the asymmetry at the running energy, before the pole correction.

The combined result corresponds to $\sin^2\theta_{\mathrm{eff}}^{\mathrm{lept}} = 0.23097
\pm 0.00027$ [@abe2000alr]. Its relative statistical error is about 1.3%, and in 1997–98
the 0.64% relative systematic error came mostly from the polarisation (0.50%) and the beam
energy (0.39%) [@abe2000alr; @schael2006zpole]. The difference between the 1996 and 1997–98
polarisations comes from the photocathodes of the polarised source [@abe2000alr].

## Leptons and heavy quarks

The leptonic analysis fits the polarised angular distribution of each lepton-pair final
state event by event. The left-right asymmetry gives $\mathcal{A}_e$ in every channel, and
the left-right forward–backward asymmetry gives $\mathcal{A}_\mu$, $\mathcal{A}_\tau$ and,
in electron pairs, $\mathcal{A}_e$ again [@abe2001lepton]. From all SLD leptonic data,
$\mathcal{A}_e = 0.1544 \pm 0.0060$, $\mathcal{A}_\mu = 0.142 \pm 0.015$ and
$\mathcal{A}_\tau = 0.136 \pm 0.015$. With lepton universality and the left-right
asymmetry, $\mathcal{A}_\ell = 0.15130 \pm 0.00207$, or
$\sin^2\theta_{\mathrm{eff}}^{\mathrm{lept}} = 0.23098 \pm 0.00026$.

For the heavy quarks, with the statistical uncertainty first and the systematic second
[@abe2005rbrc; @abe2005abac]:

- $R_b = 0.21594 \pm 0.00094 \pm 0.00074$ from 1993–98, and
  $R_c = 0.1744 \pm 0.0031 \pm 0.0020$ from 1996–98;
- SLD's average of its direct asymmetry measurements is $\mathcal{A}_b = 0.9170 \pm
  0.0147 \pm 0.0145$ and $\mathcal{A}_c = 0.6712 \pm 0.0224 \pm 0.0157$.

## The two most precise determinations

The joint LEP and SLD analysis compares six determinations of the leptonic mixing angle
(Figure 4.41). Their average is $0.23153 \pm 0.00016$, with $\chi^2/\mathrm{dof}
= 11.8/5$. The spread comes from the two most precise entries, SLD's $\mathcal{A}_\ell$ and
the forward–backward asymmetry of b quarks at LEP, which differ by 3.2 standard
deviations [@schael2006zpole]. SLD's hadronic
$A_{LR}^0$ alone lies 2.3 standard deviations above the Standard Model expectation in the
2024 review of the Particle Data Group [@erler2024pdg].

![Determinations of the effective leptonic mixing angle at the Z pole, with the average of the six (band). SLD's entry, from the left-right asymmetry and the leptonic asymmetries, is the lowest of the precise ones; the b-quark forward–backward asymmetry at LEP is the highest. The open marker is the value the released data give from the raw left-right asymmetry, without the correction to the pole, and is not comparable to the others at that level.](../figures/sld-sin2theta.svg)

## Reproduction with the released data

The 1996–1998 mini-DSTs, about 660,000 reconstructed events, were recovered and released
in 2026 [@cheng2026aiready; @zenodo]. The dataset paper applies the published hadronic and
leptonic selections without change, pools 1997 and 1998, combines the two year-groups by
inverse-variance weighting and quotes only statistical and polarisation uncertainties,
since the purpose is a consistency check [@cheng2026aiready]. Table 4.28
compares its results with the published ones.

<!-- table:repro -->
| Quantity | Released data | Published |
|---|---|---|
| Hadronic Z, 1996 / 1997–98 | 51,118 / 334,465 | 51,873 / 331,614 |
| $A_{LR}$, combined, at the running energy | $0.1477 \pm 0.0035$ | |
| $A_{LR}^0$, 1996–98 | | $0.15056 \pm 0.00239$ |
| $\mathcal{A}_e$ / $\mathcal{A}_\mu$ / $\mathcal{A}_\tau$, 1996–98 | 0.154 / 0.135 / 0.112 | 0.1549 / 0.152 / 0.121 |
| $\mathcal{A}_\ell$ | $0.137 \pm 0.008$ (lepton pairs) | $0.15130 \pm 0.00207$ (with $A_{LR}^0$) |

Table: Results of the dataset paper on the released 1996–1998 data [@cheng2026aiready] against the published SLD values [@abe2000alr; @abe2001lepton]. The published $\mathcal{A}_e$, $\mathcal{A}_\mu$ and $\mathcal{A}_\tau$ are those of the 1996–98 runs; the published $\mathcal{A}_\ell$ combines the lepton-pair results of 1993–98 with the hadronic $A_{LR}^0$ of 1992–98.

Three choices separate the two. The released-data $A_{LR}$ is the asymmetry at the
running energy; the published pole value adds a correction computed with ZFITTER, about
0.0035, which the released sample cannot repeat. The raw asymmetries $(N_L-N_R)/(N_L+N_R)$
agree with the published ones to within $4\times10^{-4}$, inside their statistical
uncertainties [@cheng2026aiready]. The leptonic results use direct counting with an
analytic correction for the angular acceptance and take $\mathcal{A}_e$ from the muon
channel; their event counts differ more from the published ones, most of all for τ pairs
[@cheng2026aiready].

## Papers, data and software

- **Dataset paper** [@cheng2026aiready]: the recovered data, their format, the
  validation and the measurements above.
- **Cross-detector transfer** [@lo2026parnassus]: a fast-simulation model trained on
  ALEPH simulation and fine-tuned on SLD simulation, which produces reconstructed SLD events
  from generator-level ones.
- **Data** [@zenodo]: the Zenodo concept record of the release, which resolves to the
  latest version. Version 1 is superseded. Version 2
  ([doi:10.5281/zenodo.21199778](https://doi.org/10.5281/zenodo.21199778)) holds the
  1996–1998 data in Jazelle and Parquet form with the documentation corpus and is the
  version the dataset paper cites. Version 3
  ([doi:10.5281/zenodo.22732257](https://doi.org/10.5281/zenodo.22732257)) adds simulated
  events.
- **Reader** [@jazellereader]: the C++ and Python reader of the Jazelle files, on PyPI as
  `jazelle`.
- **Analysis** [@sldresurrect]: the selections and measurements of the dataset paper.

!!! summary "Key points"
    - SLD's combined $A_{LR}^0 = 0.15138 \pm 0.00216$ gives
      $\sin^2\theta_{\mathrm{eff}}^{\mathrm{lept}} = 0.23097 \pm 0.00027$, the most
      precise of the Z-pole determinations.
    - SLD's $\mathcal{A}_\ell$, from the left-right asymmetry and the lepton-pair
      asymmetries, differs by 3.2 standard deviations from the LEP b-quark
      forward–backward asymmetry, the second most precise determination.
    - The released 1996–1998 data reproduce the published hadronic event counts within
      1.5% and the raw asymmetries within $4\times10^{-4}$; the pole correction is not
      applied.

## Further reading

The joint LEP and SLD report [@schael2006zpole] describes every measurement and the
combination. The dataset paper [@cheng2026aiready] gives the reproduction in full,
including the comparison of event counts by channel.
