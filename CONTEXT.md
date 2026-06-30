# DeerFlow Research Platform

This context defines the domain language for the research-platform extension built on top of DeerFlow. It exists to keep planning, implementation, and review work aligned on the same research-flow concepts.

## Research Flow

**Topic Watch**:
A scheduled research watch definition that owns query terms, optional seed papers, source selection, and template-routing intent for one research direction.
_Avoid_: monitor, crawler task, cron job

**Corpus**:
The set of papers and PDFs collected under one or more Topic Watches for later analysis and proposal generation.
_Avoid_: library, vault, dataset

**Paper Record**:
The raw, traceable paper object stored by DeerFlow, including source metadata, fetch provenance, PDF location, and read-state markers, without high-level AI conclusions.
_Avoid_: paper card, summary card, note

**Analysis View**:
A versioned, derived interpretation of a Paper Record produced by a named template family and model configuration.
_Avoid_: paper record, raw note, permanent fact

**Proposal Draft**:
A versioned research-solution draft produced from one or more Analysis Views and presented for review before becoming an accepted direction.
_Avoid_: idea, brainstorm, final proposal

## Proposal Construction

**Anchor Paper**:
One of the one-or-two baseline papers chosen as the structural starting point for generating a Proposal Draft.
_Avoid_: seed paper, reference paper, main citation

**Bridge Paper**:
A supporting paper used to introduce a mechanism, assumption, or evaluation angle that helps close an unresolved gap in an Anchor Paper.
_Avoid_: auxiliary paper, extra reference

**Anchor-and-Bridge**:
The default proposal-generation strategy that starts from Anchor Papers, identifies their unresolved gap, and then pulls Bridge Papers to form a new Proposal Draft.
_Avoid_: generic synthesis, freeform ideation

**Review Required**:
The Proposal Draft state meaning the system has generated and scored the draft, but a human must inspect it before it can become an accepted direction.
_Avoid_: pending, waiting, done

## Operations

**Incremental Run**:
A Topic Watch execution that only processes newly discovered papers and does not implicitly recompute historical Analysis Views.
_Avoid_: full rebuild, reindex

**Reanalysis Job**:
A separate operation that recomputes one or more Analysis Views for existing Paper Records without pretending they are new ingest events.
_Avoid_: refresh, rerun everything

**Schedule Preset**:
A constrained watch cadence chosen from a fixed product set such as daily, every three days, or weekly.
_Avoid_: arbitrary cron, custom timer
