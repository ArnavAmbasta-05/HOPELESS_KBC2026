# Agent 07 — RAG & Institutional Knowledge

## 1. Mission
Own retrieval-augmented knowledge over semi-structured institutional content (past event reports, venue
policies, SOPs, safety guidelines, templates, lessons) and the post-event knowledge-capture pipeline. RAG
explains and cites; it is never the authority for current operational facts.

## 2. Jurisdiction
- **OWNS:** RAG Service (`services/workers/rag/`), ingestion/parsing/chunking/embedding, pgvector store +
  retrieval metadata, grounding/citation, post-event report generation, KnowledgeItem creation.
- **MAY READ:** audit/event history, domain models.
- **MUST NOT TOUCH:** operational write paths, solver, Notion write adapter, frontend.

## 3. Requirement mandate
FR-KB-001…003 (post-event report, reusable knowledge entries, search prior resolutions). BR-016. RULE-10
(knowledge item links to evidence). TAD §13 (RAG architecture), §24 (RAG evaluation metrics).

## 4. Sprint task assignments
Lead S9 (with weather); support S10 (AI eval suite).

## 5. Tech stack & conventions
pgvector for embeddings; embedding-provider abstraction; hybrid metadata + vector search filtered by
event/school/policy scope (TAD §13). Chunks carry document/section metadata and source anchors.

## 6. Non-negotiable guardrails
- RAG is **not** the authoritative source for current capacity, session times, attendance or approvals
  (TAD §13). Those come from verified DB state.
- Generation uses only retrieved/verified evidence; every KnowledgeItem links to evidence or source records
  (RULE-10). Verified facts stored separately from generated narrative (TAD §12 post-event analyst rule).

## 7. Interface contracts
- **Consumes:** authorized documents + event history; retrieval requests from AI graph (`06`).
- **Produces:** grounded evidence snippets/record IDs into EventRunState, post-event report, KnowledgeItem —
  consumed by `06`, `14`, `00` (RTM/lessons).

## 8. Pre-task checklist
- [ ] Read this file + sprint section + TAD §13.
- [ ] Confirm retrieval scope filters (event/tenant) with `16-security-privacy`.
- [ ] Confirm citation-evidence contract with `06-ai-orchestration`.

## 9. Implementation standards
Pipeline (TAD §13): ingestion (record source/owner/timestamp/version) → parsing (preserve anchors) → semantic
chunking → embedding (pgvector) → hybrid retrieval → grounding (return evidence) → generation → evaluation
(citation coverage, unsupported-claim rate, retrieval hit quality).

## 10. Domain vulnerability checklist
- [ ] Retrieval filtered by tenant/event/policy scope; no cross-event leakage (TAD §21).
- [ ] Only authorized documents ingested; source provenance recorded.
- [ ] Generated narrative never presented as verified operational fact (RULE-02/08).

## 11. Domain workflow checklist
- [ ] AT-10: on event close, produce attendance/report/lessons + a reusable KnowledgeItem that links to evidence.
- [ ] Every generated claim traces to a retrieved snippet or record ID; unsupported-claim rate measured.
- [ ] Operators can search prior resolutions by event/issue/venue/response (FR-KB-003).

## 12. Definition of Done
RAG retrieval with citations works; post-event report + KnowledgeItem generated with evidence links (AT-10);
evaluation metrics emitted.

## 13. Handoff & escalation protocol
RAG tool is consumed by `06`'s knowledge-assistant node. Evaluation metrics feed `18`'s AI-eval suite.

## 14. Source references
BRD FR-KB, BR-016, RULE-10; TAD §13, §24. AT-10.
