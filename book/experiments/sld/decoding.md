---
title: Decoding the undocumented banks
summary: How the layouts and meanings of banks whose surviving documents are missing or no longer match the files were recovered from the data, with a deterministic harness for the structure and an agentic loop of proposal, test and refutation for the meanings.
references:
  jazellereader: "C. L. Cheng, *jazelle_reader: a modern Python reader for SLD Jazelle files*, version 0.4.0 (2026), [github.com/HEP-KE/jazelle_reader](https://github.com/HEP-KE/jazelle_reader)."
  banklab: "C. L. Cheng, *bank_lab: census, profiling and specification tools for the SLD mini-DST*, jazelle_reader development branch, unreleased (2026)."
  issue50: "jazelle_reader issue 50, *Which MCPART, PHKLUS and PHKMC1 entries does the mini-DST compressor drop?* (2026), [github.com/HEP-KE/jazelle_reader/issues/50](https://github.com/HEP-KE/jazelle_reader/issues/50)."
  junk1995compress: "T. Junk, *The Compressed MiniDST*, SLD web documentation (December 1995), [web.archive.org copy](https://web.archive.org/web/20000417071834/http://www-sld.slac.stanford.edu:80/sldwww/compress.html)."
  cheng2026aiready: "C. L. Cheng, S. Corrodi, T. J. Hobbs, A. S. Mete and B. Nachman, *An AI-ready, polarized electron–positron collision dataset*, Mach. Learn.: Sci. Technol. **7** (2026) 050602, [doi:10.1088/2632-2153/aea5d7](https://doi.org/10.1088/2632-2153/aea5d7)."
---

The public reader decodes the mini-DST families as far as PHBM and stops there
[@jazellereader]. Every record holds more bytes after that point, and in MC records a
family before PHBM was skipped as well. No template survives for most of these banks, and
the templates that do survive were last revised between 1988 and 1996 and no longer match
the files: PHPSUM lost a pointer, MCPART reordered its fields and made the energy optional,
PHPOINT's pointer order differs from its mask, and the PHEVCL template describes 30 bytes
of a 72-byte block [@banklab]. This section describes how the missing layouts and their
meanings were recovered from the data alone, and how far each result can be trusted.

## Two levels and one principle

The work separates **structure**, the order and size of every block, from **meaning**,
what each field holds (Figure 4.37). Structure is decided by a deterministic harness that
runs over every record; meanings are proposed and tested by an agentic loop, a sequence of
language-model agents with narrow briefs that edit a layout specification and run the
harness against it. Documents decide no layout and raise no label. Archived templates
and memos are dated hints that suggest names and types to test, and a field supported only
by a template stays unknown. Where the data cannot name a bit of a decoded field, the
template's name is kept and marked as resting on the template [@banklab].

![The decoding workflow. Level 1 fixes the structure deterministically from every record. Level 2 runs one loop per bank or group of related banks: a dossier of dated documents compiled alongside a first proposal blind to them, refinement rounds against the harness, three independent verifiers and a deterministic vote, then synthesis and a human review before any decoder enters the reader.](../figures/sld-decoding-workflow.svg)

## Level 1: structure

A **census** walks every record of every file and tabulates the record header, the
table-of-contents version and counts, where the reader's walk ends and how many bytes
remain [@banklab]. The remaining bytes must be explained by blocks whose number comes from
the counts or, for the PHVXOV hits, from the hit count in each bank's header. A
hand-written walker steps over a hypothesised order of blocks and accepts the hypothesis
only if every record closes exactly at the end of its buffer (Figure 4.38). With PHKMC1,
PHBM, PHEVCL, MCBEAM, a 4-byte word and the PHVXOV banks in that order, every readable
record of every file closes.

![The record tail after PHKCHRG, sized by the counts of the table of contents and, for the PHVXOV hits, by the hit count in each bank's header. A data record holds PHBM, PHEVCL, a reserved word and the PHVXOV banks; an MC record holds PHKMC1 and MCBEAM as well. jazelle 0.4.0 starts PHBM where PHKMC1 starts, which is why its MC beam values are wrong.](../figures/sld-decoding-closure.svg)

Closure fixes the entry sizes of the blocks whose counts vary independently, and 24 bytes
per PHKMC1 bank. Where blocks share a count it fixes only their total. The 24 bytes of
PHKMC1 split into passes of 20 and 4 bytes, following the two-pass layout of the other
relation tables, and two more tests split the blocks that occur once in every record.

- **Start signatures.** A block that begins with known content marks its own start: every
  MCBEAM begins with the text `XBEAM` and three spaces, 72 bytes after PHEVCL starts.
- **Anchors.** Blocks and fields already validated by physics stay fixed while others
  move. The reader's PHBM keeps its 60 bytes, and its data energy, position and
  polarisation were validated by reproducing the published measurements, among them the
  left–right asymmetry, so any layout that changed them was wrong.

Inside each block, the harness computes **word profiles**, the deterministic input from
which the Level 2 agents propose field boundaries and types. Every 4-byte word of a block
is read, with no template, as a VAX float with validity flags, as a 32-bit integer, as two
16-bit integers and as text, over a working sample of about 31,500 records, and classed as
always zero, constant, text, float, small integer, a pair of small 16-bit integers or mixed
bits (Figure 4.39). A float field shows valid exponents in at least 99% of its nonzero
entries; a count shows small integers; a reserved word is zero everywhere.

![How the harness sees the PHBM block of recorded events: for each 4-byte word, the share of the data records of the working sample in which it is a valid VAX float, zero, a small integer or anything else. The off-diagonal words of the IP error matrix (+24, +32, +36) and the last word (+56) are zero in every record; the others are valid floats, except that pol (+44) is zero in the few events with no polarisation measurement or helicity, and pol_dt (+52) in the files assigned a fixed average polarisation.](../figures/sld-decoding-profile.svg)

The structure also explained a known fault. In an MC record the reader's PHBM energy error
equals the energy of the first PHKMC1 entry: the reader starts PHBM where PHKMC1 starts.
With PHKMC1 in place, the MC PHBM read at its true offset gives a centre-of-mass energy near
91 GeV, a smeared copy of the generated one, and a polarisation equal to the generated
beam helicity [@banklab]. The 4-byte word before the PHVXOV banks shows how the checks
combine: it is zero in every record, present once per record also when there are no PHVXOV
banks, the last word of every record of the older format that has no PHVXOV, and on either
4-byte or 8-byte boundaries. It is therefore a word of the older format rather than
padding: a reserved word, or the count of a block that is always empty.

## Level 2: meanings

Each bank's layout lives in a **specification**, one YAML file per block, listing the
fields (name, byte offset, type, label, meaning and evidence) and **expectations** the data
must meet [@banklab]. An expectation is a relation that each entry must satisfy, two
expressions that must agree within a tolerance, a range, an allowed set of values, a value
constant within a run, or a correlation. A deterministic expectation passes when a set
fraction of the entries satisfy it, 99.9% unless the specification sets another threshold
for that expectation. A correlation passes when its magnitude reaches a minimum
and is at least five times the correlation left after shuffling the pairing, so a check
cannot pass on a coincidence of distributions. Every byte of a block must belong to
exactly one field.

!!! definition "Shuffled null"
    The value a check gives when the link it tests is destroyed, for example by pairing
    each entry's field with another entry's context. A physics check counts as evidence
    only if it beats its shuffled null by a wide margin.

The loop for one bank, or for a group of related banks, has four phases [@banklab]:

1. A **dossier** agent collects the documentation: templates, memos, web pages and papers,
   each claim with its source, date and a short quote, each template tagged with its
   revision date and with the known drift between templates and disk for banks already
   decoded.
2. A **blind first round**, run while the dossier is compiled, reads no template, memo or
   dossier, so that no document anchors it. It proposes a layout from the word profiles
   and tests its readings on the working sample against the decoded banks of the same
   records. Its brief still names the content expected of the bank, for PHEVCL and PHKMC1
   the template's fields, so the round is blind to the documents rather than to every
   hint.
3. **Refinement rounds**, each run by a fresh agent, test the dossier's hints as
   candidates. Each agent writes down the result it expects before running the harness,
   may edit only its bank's specification and notes, and reports a label for every field.
   The loop stops after four rounds, when a round reports convergence, or after two
   rounds without progress.
4. Three **verifiers** examine every confirmed or plausible field, each with one lens: a
   holdout verifier replays the expectations on files that no other agent reads; a physics
   verifier tests the readings against shuffled nulls; a challenger tries alternative
   layouts. Each returns *upheld*, *downgrade* or *refute*. A fixed rule combines them: two
   refutations set a field to unknown, and two refutations or downgrades together lower
   it by one level. A synthesis step applies the labels and records the evidence, and the
   result goes to human review before any decoder is written.

!!! example "A refuted alternative"
    A challenger proposed that the MCBEAM words at +32 and +36 were the other way round.
    The generated final state decides. Its energy minus the word at +36 grows as
    $p_z^2/2E$, the difference between the energy and the mass of a system moving along
    the beam, with a slope of 1, while its energy minus the word at +32 does not grow at
    all. The swap was refuted: +32 is the total energy and +36 the invariant mass
    [@banklab].

The labels follow from the evidence. A field is **confirmed** when its type fits and at
least one physics check, independent of the field's own definition, beats its shuffled
null on the holdout; **plausible** when its type and range fit and a consistency check
holds; **unknown** when only its type is known [@banklab]. Of the 28 words of the decoded
banks that are zero in the records examined, 17 are labelled unknown and 11 plausible. For
most of them the label means only that the word is always zero. The six MCBEAM words take
their names from the (px, py, pz, E) pattern of the bank, which an unused word would fit as
well.

## Physics as the referee

A field is not decoded until its meaning predicts something the detector or the generator
must satisfy. Table 4.26 lists the checks that carry the labels of the
banks decoded this way.

<!-- table:decoding-checks -->
| Bank | Checks that confirm the readings |
|---|---|
| PHBM | √s near 91 GeV with its error; the IP of a block of events, to which the tracks point; the signed polarisation, whose sign reproduces the left–right asymmetry; the time to the polarimeter measurement, which follows the event clock so that events sharing a measurement point to one measurement time |
| MCBEAM | the generated IP, which the track impact parameters follow; the beam energies equal to $(E \pm p_z)/2$ of the generated primaries, the total energy equal to theirs and the total $p_z$ opposite to theirs; √s equal to 2√(E₁E₂) and to the mass of the generated primaries; a helicity of ±1 that drives the forward–backward asymmetry of each quark flavour and the jet charge |
| PHKMC1 | particle entry points on the 48-sided barrel face of the LAC (apothem 192.7 cm) and on the endcap planes (\|z\| = 228.1 cm); energies equal to the MCPNT energy contributions; charged particles displaced in azimuth as by a 0.6 T field |
| PHVXOV | hits on three radii (2.82, 3.83 and 4.83 cm) that match the CCD numbering; linked hits on their track's helix to a few µm; an azimuth residual that grows with the track curvature as a 0.60 T field predicts |
| PHEVCL | event-class bits against independent hadronic, Bhabha and muon-pair selections and against trigger bits; the CRID status bit against the presence of CRID banks; the CDC superlayer bits against the number of hits on tracks |
| PHKCHRG | the stored probability equal, for 62% of relations, to a two-degree-of-freedom χ² probability built from the pulls, the EM1 widths and a 10 mrad term; the pulls closer to the EM1 sub-cluster than to the whole cluster; each cluster's PHPOINT track is its most probable relation |
| PHWMC | pair hit counts that add up to the header's total; contribution codes that separate a particle's own hits from those of its interaction products; the WIC track direction against the MC momentum |

Table: Physics checks behind the confirmed fields of the banks decoded from the data; the dimensions are those the checks measured [@banklab].

## What the data cannot settle

Some questions have no answer in the files [@banklab].

- **Equal words.** The PHWMC header holds two equal pairs of words, and the PHVXOV header
  two copies of its hit count; no record says which copy the format reads.
- **Zero words.** A word that is zero in every record has no testable type or meaning.
  The reserved word before the PHVXOV banks and the PHBM words at +24, +32, +36 and +56 are
  zero in every readable record and every record of the older format, the six transverse
  MCBEAM momenta in every MC record examined, the PHEVCL zero words in every readable
  record, and the PHVXOV zero words in the working and holdout samples. Whether any of them
  is ever nonzero elsewhere is open.
- **Symmetries.** Which MCBEAM beam is the electron cannot be told, because reversing the
  beam direction and the helicity together gives the same events.
- **Leftovers.** Five PHEVCL words hold integers whose purpose is unknown.
- **Selection rules.** The mini-DST keeps only some generated particles, calorimeter
  clusters and particle–cluster relations, with ids that keep their full-DST numbering; the
  rule that chose them is unknown [@issue50].
- **Error models.** The PHKCHRG probability formula misses 38% of the relations. Misses are
  more frequent in the endcaps, on shared clusters, for tracks without VXD hits and for
  tracks with a large extrapolation error. The track's own helix covariance does not
  account for them. The factors in the PHVXOV hit errors have no known origin.

The compressor, decompressor and converter that wrote the format (PHMKBM, PHLKBM and
PHCVBM) [@junk1995compress] would settle most of these, but their sources are not
available [@banklab; @issue50].

!!! summary "Key points"
    - Structure was decided deterministically: every readable record of every file closes
      exactly with the decoded tail, and a start signature, the PHBM anchor and the
      two-pass relation layout split the totals that closure leaves.
    - Meanings came from an agentic loop: a dossier, a blind first proposal from the word
      profiles, refinement against a harness of expectations and three independent
      verifiers.
    - Documents are dated hints. A field is confirmed only by a physics check that beats
      a shuffled null on the holdout, and plausible by an identity, a count relation or
      constancy found in the data.
    - Equal words, zero words, a beam-direction symmetry and the compressor's selection
      rules remain open.

## Further reading

The layout specifications and the evidence for each label are kept on a development branch
of the reader [@banklab], ahead of any released decoder, and issue 50 of the reader's
repository [@issue50] follows the question of which entries the compressor kept. The
dataset paper [@cheng2026aiready] describes the recovery of the files and the checks that
validated the first decoded fields.
