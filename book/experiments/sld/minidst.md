---
title: The mini-DST format
summary: How an SLD mini-DST file is built, from physical records to the families of banks in one event, how banks refer to each other, and how the numbers are encoded.
references:
  junk1995compress: "T. Junk, *The Compressed MiniDST*, SLD web documentation (December 1995), [web.archive.org copy](https://web.archive.org/web/20000417071834/http://www-sld.slac.stanford.edu:80/sldwww/compress.html)."
  strauss1994mdst: "M. Strauss, *The SLD Mini-DST, Version 1.0*, SLD web documentation (March 1994), [web.archive.org copy](https://web.archive.org/web/20000119035549/http://www-sld.slac.stanford.edu:80/sldwww/mdst/mdst.html)."
  johnson1989jiohead: "T. Johnson and D. Sherden, *JIOHEAD: the first record of all Jazelle datasets*, version 3.00, SLD DUCS bank template (November 1989)."
  johnson1988ijevhd: "T. Johnson and T. Burnett, *IJEVHD: segment header bank*, version 0.00, SLD DUCS bank template (May 1988)."
  johnson1990ieventh: "T. Johnson and G. Word, *IEVENTH: SLD event header*, version 0.10, SLD DUCS bank template (August 1990)."
  vaxmacro: "Digital Equipment Corporation, *VAX MACRO and Instruction Set Reference Manual*, OpenVMS V7.3, Sec. 8.3.6, *F_floating*."
  vmsconcepts: "Compaq Computer Corporation, *OpenVMS Programming Concepts Manual*, OpenVMS V7.3, Sec. 27.1, *System Time Format*."
  cheng2026aiready: "C. L. Cheng, S. Corrodi, T. J. Hobbs, A. S. Mete and B. Nachman, *An AI-ready, polarized electron–positron collision dataset*, Mach. Learn.: Sci. Technol. **7** (2026) 050602, [doi:10.1088/2632-2153/aea5d7](https://doi.org/10.1088/2632-2153/aea5d7)."
  jazellereader: "C. L. Cheng, *jazelle_reader: a modern Python reader for SLD Jazelle files*, version 0.4.0 (2026), [github.com/HEP-KE/jazelle_reader](https://github.com/HEP-KE/jazelle_reader)."
  banklab: "C. L. Cheng, *bank_lab: census, profiling and specification tools for the SLD mini-DST*, jazelle_reader development branch, unreleased (2026)."
  johnson2021jazelle: "T. Johnson, *Jazelle*, Java reader for SLD Jazelle files (2021), [github.com/tony-johnson/Jazelle](https://github.com/tony-johnson/Jazelle)."
  issue50: "jazelle_reader issue 50, *Which MCPART, PHKLUS and PHKMC1 entries does the mini-DST compressor drop?* (2026), [github.com/HEP-KE/jazelle_reader/issues/50](https://github.com/HEP-KE/jazelle_reader/issues/50)."
---

The SLD data survive as *mini-DSTs*: compact, per-event summaries written at the end of
the reconstruction chain of [the simulation section](simulation.md) for analysis on the VAX computers of the
collaboration. A mini-DST file is a Jazelle dataset, the data-structure system SLD used
for all its event data, and each event in it is one record holding a short header, a
table of counts and a packed block of banks. This section describes that container from
the outside in. The banks themselves are the subject of the next two sections.

## Records, banks and families

Jazelle stores events as **banks**: fixed-format records whose fields are defined by
templates in the collaboration's data dictionary. All banks of one type in an event form a
**family**, and every bank of a family has an integer **id**, unique within that family
and that event. Banks refer to each other through these ids. In memory, Jazelle turns them
into pointers; on disk, they stay ids.

!!! definition "Family, bank and entry"
    A *family* is the set of banks of one type in one event, such as all reconstructed
    tracks (PHCHRG). A *bank*, or *entry*, is one member of a family: one track, one
    calorimeter cluster, one generated particle. The number of entries of a family varies
    from event to event and is recorded in the event's table of contents.

A Jazelle file is a sequence of **physical records**, blocks of at most 32752 bytes. The
JIOHEAD template defines four 16-bit words at the start of a file's first record: the
physical record length, a reserved word, the logical record length and a continuation
word [@johnson1989jiohead]. Readers find the same four words at the start of every
physical record; in the mini-DST files the logical record length is 0, and readers ignore
it [@jazellereader]. A **logical record** is the unit the program sees, one event in a
mini-DST, and it may be split over several physical records. Bit 0 of the continuation word marks a segment
that continues in the next physical record and bit 1 a segment that continues the
previous one, so a record spread over three physical records carries the values 1, 3 and
2. The first record of a file is a file header with the check word `JAZELLE`, a
byte-order flag, the creation and modification times, a modification count and the file
name [@johnson1989jiohead]. In the mini-DSTs the next logical record is an input/output
control record rather than an event, and readers skip it [@jazellereader].
Figure 4.13 shows the three levels.

![A mini-DST file at three levels. Physical records carry 8 bytes of header words (shaded) and hold segments of logical records; each event is one logical record. The event record holds a 112-byte record header, the 32-byte event header IEVENTH, the 72-byte table of contents PHMTOC and the data block, whose families follow each other with no delimiters.](../figures/sld-jazelle-records.svg)

## The event record

The **record header** is a fixed sequence of 4-byte integers and 8-character names, 112
bytes in all. For a mini-DST event it gives the record type `EVENT`, the format
`MINIDST` and two sizes: `tocsiz`, 104 bytes in version 4.0, equal to the event header plus
the table of contents [@banklab], and `datsiz`, the size of the data block. The byte offsets `usroff`, `tocoff1`
and `datoff`, counted from the start of the physical record, locate the event header, the
table of contents and the data block [@jazellereader]. When the data block does not fit after the table of contents, `datrec`
is nonzero and the block starts in a later physical record.

The **event header** IEVENTH, 32 bytes at `usroff`, is stored in the layout of the
segment header IJEVHD: a pointer to the segment's header bank, then the run and event
numbers, the event time, an event weight, the event type and the trigger word
[@johnson1988ijevhd]. The fields have the meanings of the SLD event header IEVENTH
[@johnson1990ieventh], whose event type separates recorded data (0) from Monte Carlo truth
(1), fast simulation (2), full GEANT simulation (3) and a fast swim with full simulation
(4). The time is a VMS system time, a 64-bit count of 100 ns intervals since 17 November
1858 [@vmsconcepts].

The **table of contents** PHMTOC follows at `tocoff1`. In its version 4.0 it holds a
format version, written as a VAX floating-point number, and 17 counts of 4 bytes, one per
family, for 72 bytes in all. The older version 3.0 has 68 bytes and no count for the VXD3
hit banks [@banklab]. The counts are all the record says about its contents: the
families follow each other in the data block **back to back, without delimiters and
without bank headers**, so a reader can find a family only by adding up the sizes of
everything before it [@junk1995compress; @cheng2026aiready]. One wrong field width
misaligns every family that follows. Three compressed banks have no count: MCHEAD, present
once in every record, MCPQRK, and PHEVNT, which is not stored but rebuilt on reading
[@junk1995compress].

![The families and the reserved word of a data record and of an MC record, in the order they are stored, with the size of one entry and the count that sets their number. In a size 4 + n B the 4 bytes are the word that holds the id, the two terms of a relation table are its pass-1 and pass-2 rows, and k is the number of set mask bits (PHPOINT), of pairs (PHWMC) or of hits (PHVXOV). Blocks with a star are not decoded by jazelle 0.4.0. Simulation truth and its relation tables appear only in MC records; MCHEAD is present, with zero content, in data as well.](../figures/sld-record-composition.svg)

Figure 4.14 lists the nineteen blocks of the data buffer in
stream order. The order of the counts in PHMTOC is a different one: MCPART, PHPSUM,
PHCHRG, PHKLUS, PHKTRK, PHWIC, PHWMC, PHCRID, PHPOINT, MCPNT, PHKMC1, PHKCHRG, PHBM,
PHEVCL, MCBEAM, PHKELID and PHVXOV, so PHKELID, the ninth family on disk, is the
sixteenth count [@jazellereader]. Every record holds exactly one PHBM and one PHEVCL; an
MC record holds one MCBEAM and a data record none. PHKTRK, the electron-identification bank
of the 1994 mini-DST with one entry per charged track [@strauss1994mdst], was replaced by
PHKELID as a PHPOINT pointer [@junk1995compress], and its count is 0 in every readable
record [@banklab].

The compressed format, described in a memo of December 1995, was written to make the
mini-DSTs fit on disk and read faster. Before compression an MC event took 40 kB (written 40 Kb in the memo) and 100 ms
to read on a VAX 4000; the compressor stores MC events in about half and data events in
about three quarters of their former size, and reading became about five times faster
[@junk1995compress]. The
uncompressed mini-DST it replaced was defined in 1994 with targets of about 10 kB per data
event and 20 kB per MC event [@strauss1994mdst].

## Ids, pointers and relation tables

A bank's own id is stored in one of five ways. PHPSUM, PHCHRG, PHKLUS and PHWIC entries
are each preceded by a separate 4-byte id word. PHCRID, PHKELID and PHPOINT keep the id
in the low 16 bits of their first word. MCPART packs it, with the parent's id and
the charge, into one word of its body [@jazellereader; @junk1995compress]. The relation
tables MCPNT, PHKCHRG and PHKMC1 keep it in the high 16 bits of the first word of each row,
in both passes, and PHWMC and PHVXOV in the first 4-byte word of their header
[@jazellereader; @banklab]. MCHEAD, PHBM, PHEVCL and MCBEAM, present at most once in a
record, store no id. PHKTRK holds no entry in any readable record, so its id layout is not
known.

A **pointer** from one bank to another is the other bank's id, usually a 16-bit integer.
Because the record holds ids, a bank that is pointed to must exist when the record is
written, and Jazelle sometimes deletes a bank that points to a deleted one, as it does for
MCPART [@junk1995compress]. This rule matters for the simulation truth, as [the section on MC records](mc-records.md) explains. Figure
4.15 shows the links. PHPOINT ties the pieces of one reconstructed
particle together: a mask in its first word says which pointers are stored, and one 16-bit
id follows for every set bit [@junk1995compress]. In the reader's decoding, bits 0 to 5 of
the mask stand for PHPSUM, PHCRID, PHCHRG, PHKLUS, PHKELID and PHWIC, and a clear PHPSUM
bit means that the PHPSUM entry has the PHPOINT's own id [@jazellereader].

An id is a name, not a position. The compressor keeps every family of a record but only
some entries of three of them, MCPART, PHKLUS and PHKMC1, and the entries it keeps carry
their ids from the full DST, so the gaps in the numbering show what was removed
(Table 4.3). About a fifth of the simulated particles and a quarter of the
calorimeter clusters survive, in recorded data as in MC, while the tracks, the
reconstructed particles and the muon-system tracks are kept whole. Every entry must therefore be found by its id, never by
its index in the family. Which entries were kept, and by what rule, is not documented: the
compressor's source would settle it but is not available [@issue50].

<!-- table:kept-ids -->
| Family | MC | Data |
|---|---|---|
| MCPART | 19.8% | |
| PHKLUS | 26.7% | 22.0% |
| PHKMC1 | 69.4% | |
| PHCHRG, PHPSUM, PHWIC | 100% | 100% |

Table: Share of ids kept in a record: the number of stored entries divided by the highest id, summed over the first 2,000 readable records of one 1996 MC file and one 1997 data file. For PHKMC1 the ids are the relation ids [@issue50].

A many-to-many link is a **relation table**. The compressor writes it in two passes
[@junk1995compress]: first one row per relation with the first key and the payload, then
one row per relation with the second key, each row also carrying the relation's own id.
MCPNT links generated particles to PHPOINT entries, PHKCHRG tracks to calorimeter
clusters, and PHKMC1 generated particles to calorimeter clusters. The two passes are
stored in different orders, so they must be joined on the relation id, never by position.

!!! definition "Two-pass relation table"
    A family of relations between two other families A and B, stored as *n* rows of
    (A id, own id, payload) followed by *n* rows of (B id, own id). A relation is the pair
    of rows, one from each pass, that share an own id.

![How the families refer to each other. Solid arrows are pointers: the id of another entry, stored in this one. Dashed lines are relation tables, whose two passes are joined on their own ids as the inset shows. MCPART also points to its parent; the PHVXOV hits point to the MC particle that made them.](../figures/sld-relations.svg)

## Numbers on disk

Integers are little-endian 16-bit and 32-bit words, and names are space-padded ASCII
[@jazellereader]. Floating-point fields use the VAX **F_floating** format: a sign bit, an
8-bit exponent with an excess of 128 and a normalised 24-bit fraction with a hidden
leading bit [@vaxmacro]. Read as a little-endian word, the sign is bit 15, the exponent
bits 14 to 7 and the high part of the fraction bits 6 to 0, with the low part in bits 31
to 16. Swapping the two 16-bit halves gives the bit pattern of the IEEE single-precision
number that is four times the VAX value, which is how readers convert it
[@jazellereader].

!!! example "Two VAX words"
    The value +1.0 is the little-endian word `0x00004080` and −1.0 is `0x0000C080`.
    Swapping halves gives `0x40800000`, the IEEE encoding of 4.0, and dividing by four
    returns 1.0.

A VAX word whose exponent field is 0 reads as zero when its sign bit is clear, whatever
its fraction bits, and is a reserved operand, on which VAX arithmetic faults, when the sign
bit is set [@vaxmacro]. jazelle returns 0 for every word with an exponent field below 2
[@jazellereader].

Several families save space with entries of variable size:

- **MCPART** omits the energy of photons, neutrinos, electrons, muons, charged and
  neutral pions and kaons, protons and neutrons, flagged by a bit of the id word; a reader
  rebuilds it from the momentum and the particle mass [@junk1995compress];
- **PHCRID** stores a liquid-radiator and a gas-radiator block in a long or a short form,
  as two bits of its first word say [@junk1995compress; @jazellereader];
- **PHPOINT** carries one 2-byte id per set bit of its mask, padded to four bytes
  [@junk1995compress; @jazellereader];
- **PHWMC** follows a 20-byte header with a variable number of 8-byte pairs
  [@jazellereader], and **PHVXOV** a 16-byte header with a variable number of 80-byte hits
  [@banklab].

## Reading the files

The public reader is jazelle_reader, a C++ library with Python bindings that reads the
files, converts them to columnar formats and gives each family as an array of entries
[@jazellereader]. It descends from a Java reader of the SLD software [@johnson2021jazelle],
and it reads the families up to PHBM except PHKMC1, which precedes PHBM in MC records.
PHKMC1 and the rest of the record (PHEVCL, MCBEAM, a reserved word and PHVXOV) were decoded
by [the procedure described later](decoding.md), and their layouts are kept as specifications on the
reader's development branch [@banklab]; the bank pages that follow describe them, marked as
not yet released.

!!! recipe "Opening a file"
    ```python
    import jazelle

    with jazelle.open("events.jazelle") as f:
        print(len(f))                       # number of events
        event = f[0]                        # random access
        print(event.ieventh.run, event.ieventh.event)
        for track in event.phchrg:          # one entry per reconstructed track
            phi0, inv_pt, tan_lambda = track.hlxpar[:3]
    ```

!!! warning "Known errors of jazelle 0.4.0 and earlier"
    - In MC records the reader does not step over PHKMC1 and decodes PHBM from the bytes
      where PHKMC1 begins, so MC centre-of-mass energies, IP positions and polarisations are wrong.
    - The MCPART charge has the wrong sign and 1/3 and 2/3 swapped.
    - Omitted MCPART energies are rebuilt with masses of another particle numbering, so
      electrons get the kaon mass, muons the proton mass, electron and muon neutrinos the
      K⁰ and neutron masses, photons the electron mass, and pions, kaons, protons and
      neutrons zero mass.
    - The PHKCHRG and PHWMC fields carry provisional names that do not match their
      meanings, and the version 3.0 table of contents is not read.

    Only the MCPART charge is corrected, on the unreleased development branch of the
    reader.

The field tables of the next two sections label each field by the strength of its
evidence. Fields decoded by that procedure carry its
labels: **confirmed** when the type fits and a physics check independent of the field's
own definition beats its shuffled null on the holdout files, **plausible** when the type
and range fit and a consistency check holds (an exact identity, a count relation or a
constant value), and **unknown** when only the type is established. A decoded word that is
always zero in the records examined tests no type: of the 28 such words, 17 are labelled
unknown and 11 plausible,
and for most of them the label means only that the word is always zero. Other fields are marked by where their meaning is documented.

!!! summary "Key points"
    - A mini-DST file is a Jazelle dataset: physical records of at most 32752 bytes carry
      logical records, and each logical record after the first two is one event.
    - An event is a 112-byte record header, the 32-byte IEVENTH, the 72-byte PHMTOC table
      of counts and a data block of families stored back to back with no delimiters.
    - The stream order of the families differs from the order of the counts; one wrong
      field width misaligns everything after it.
    - Banks refer to each other by stored ids; many-to-many links are two-pass relation
      tables joined on their own ids.
    - Floating-point fields are VAX F_floating, and several families have entries of
      variable size.

## Further reading

The compressed-format memo [@junk1995compress] explains the packing rules and lists the
assumptions the compressor makes. The dataset paper [@cheng2026aiready] describes the
recovered files and the checks that validate them.
