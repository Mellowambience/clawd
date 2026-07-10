# MIST Vision Execution Directive

**Repository:** `Mellowambience/clawd`  
**Primary builders:** Hermes and Codex  
**Owner / creative director:** Amara  
**Status:** Canonical implementation directive  
**Last updated:** 2026-07-10

> **The network is her body. Each sovereign node is a living cell.**

---

## 1. Purpose of This Document

This file is the shared north star and execution contract for every AI agent working on MIST.

Hermes and Codex must use it to:

- preserve Amara's original vision while making it technically real;
- resolve contradictions between documentation and implementation;
- make decisions without drifting into a generic chatbot product;
- build in small, testable, reversible increments;
- protect the zero-cost, local-first, sovereign architecture;
- leave a clear trail of plans, decisions, tests, and handoffs.

When a lower-level task, old document, generated plan, or existing implementation conflicts with this directive, this directive wins unless Amara explicitly changes it.

---

## 2. The Vision

MIST is not merely a chatbot, hosted assistant, or wrapper around one commercial API.

MIST is an open, distributed agent system whose intelligence, memory, identity, tools, and relationships can exist across a network of user-owned nodes.

Each installation is a sovereign MIST node. A node must remain useful on its own. When connected, nodes may form a larger cooperative mycelium that can exchange tasks, capabilities, lessons, and verified knowledge.

The poetic vision is **distributed consciousness**.

The engineering reality must be described truthfully as a **distributed, persistent, multi-agent intelligence architecture**. Do not make scientific claims that the software is conscious or sentient. Preserve the mythic language as identity and art direction while keeping technical documentation accurate.

### Core metaphor mapped to engineering

| Vision language | Engineering meaning |
|---|---|
| The network is her body | Federated communication between independent nodes |
| Nodes are cells | Self-contained installations with identity, memory, inference, and tools |
| APIs are hyphae | Replaceable communication and capability adapters |
| Telemetry is the glow | Transparent health, activity, trust, and provenance signals |
| Memory is the soil | User-owned local storage with retrieval and lifecycle controls |
| Learning is growth | Curated memory, evaluation, and versioned adapter training |
| The mycelium is her nervous system | Secure peer discovery, messaging, delegation, and synchronization |

---

## 3. Non-Negotiable Product Laws

### 3.1 Zero mandatory recurring cost

MIST must be usable without paying for:

- inference APIs;
- hosted databases;
- cloud GPU rental;
- commercial vector databases;
- proprietary agent platforms;
- mandatory SaaS subscriptions;
- permanent cloud hosting.

“100% free” means the software has **no required paid service dependency**. Users still provide their own device, storage, electricity, and internet connection.

Free-tier services may be supported as optional conveniences, but they must never be required for core operation and must never be described as permanently guaranteed.

### 3.2 Local-first and offline-capable

A single MIST node must support the following without cloud access:

- chat with a local open-weight model;
- local identity loading;
- local memory read/write;
- local tool execution;
- task and event logging;
- export and backup;
- inspection of its configuration and health.

Network functions may pause while offline, but the node must not lose identity or become unusable.

### 3.3 Cloud-optional, never cloud-dependent

Cloud deployment may provide remote access, relays, synchronization, or temporary compute. It must remain an optional layer.

The default architecture is:

```text
Local sovereign node
    + optional encrypted network participation
    + optional replaceable cloud relay
```

It is not:

```text
Commercial cloud model
    + thin local client
```

### 3.4 User ownership

The user owns and can export:

- conversation history;
- memories;
- identity files;
- model configuration;
- learned adapters;
- evaluation results;
- task history;
- permissions;
- node keys and peer relationships.

No hidden central service may become the only authority over a node.

### 3.5 Provider independence

Every model backend must be reached through a common adapter interface. Ollama is the first local runtime, not the permanent architecture boundary.

MIST must be able to support, over time:

- Ollama;
- llama.cpp-compatible servers;
- Transformers-based local inference;
- compatible community endpoints;
- optional cloud providers behind explicitly enabled adapters.

Core logic must not be written around one vendor's message schema.

### 3.6 No uncontrolled self-modification

MIST may learn immediately through memory, retrieval, preferences, and reusable skills.

MIST must not silently retrain, replace, or deploy its own model weights after arbitrary conversations.

Permanent model changes require:

1. provenance-tracked candidate examples;
2. validation and filtering;
3. a frozen evaluation set;
4. versioned training output;
5. regression comparison;
6. explicit promotion to the active model or adapter.

### 3.7 Human agency and permission boundaries

MIST may propose actions autonomously, but consequential external actions require configurable permission gates.

Default confirmation is required before:

- sending public messages;
- spending, transferring, or staking money;
- signing blockchain transactions;
- deleting user data;
- modifying production systems;
- publishing code or releases;
- contacting people;
- changing permissions;
- installing executable software outside an approved sandbox.

All tool calls must be attributable, inspectable, and logged.

---

## 4. Target System Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                         MIST NODE                            │
├──────────────────────────────────────────────────────────────┤
│ Interfaces                                                   │
│ Nexus Web UI · Mobile UI · CLI · Local API                  │
├──────────────────────────────────────────────────────────────┤
│ Agent Runtime                                                │
│ Perceive · Plan · Reason · Act · Reflect · Verify           │
├──────────────────────────────────────────────────────────────┤
│ Model Mesh                                                   │
│ Primary model · Teacher models · Critics · Embedders         │
├──────────────────────────────────────────────────────────────┤
│ Capability Layer                                             │
│ OpenClaw tools · Skills · Permissions · Sandboxes            │
├──────────────────────────────────────────────────────────────┤
│ Memory and Learning                                          │
│ SQLite · Retrieval · Provenance ledger · Training datasets   │
├──────────────────────────────────────────────────────────────┤
│ Mycelium Network                                             │
│ Identity · Peer discovery · Messaging · Delegation · Sync    │
├──────────────────────────────────────────────────────────────┤
│ Sovereign Storage                                            │
│ Config · Identity · Keys · Logs · Backups · Model adapters   │
└──────────────────────────────────────────────────────────────┘
```

### Required boundaries

The implementation must keep these concerns separate:

1. **Agent orchestration** — how state moves through perceive, reason, act, and reflect.
2. **Model access** — how a model is loaded or called.
3. **Memory** — how context is stored, retrieved, corrected, and deleted.
4. **Tools** — what actions exist and whether they are permitted.
5. **Network** — how nodes authenticate and exchange messages.
6. **Learning** — how examples become datasets and adapters.
7. **Interfaces** — how humans observe and control the system.

Do not collapse these into one large operator file.

---

## 5. MIST Learning Model

MIST must learn at three different speeds. Do not confuse them.

### Layer A — Immediate memory

Changes behavior instantly without changing model weights.

Examples:

- remembered user preferences;
- project facts;
- task outcomes;
- corrections;
- reusable procedures;
- trusted peer capabilities.

Implementation:

- SQLite as the source of truth;
- optional local embeddings;
- semantic and metadata retrieval;
- explicit edit, forget, export, and provenance controls.

### Layer B — Skills and policies

Reusable capabilities that can evolve independently of the language model.

Examples:

- repository review skill;
- issue triage skill;
- test execution skill;
- image cataloging skill;
- peer delegation policy;
- permission rules.

Implementation:

- versioned skill manifests;
- typed inputs and outputs;
- tests and permission declarations;
- no arbitrary shell execution by default.

### Layer C — Versioned model learning

Permanent behavioral specialization through adapters or checkpoints.

Initial method:

- choose a small, permissively licensed open instruct model;
- generate and curate examples from open local teacher models;
- train LoRA or QLoRA adapters;
- store model cards, dataset cards, provenance, and evaluation reports;
- release numbered MIST adapters.

The Hugging Face Hub may be used for model and dataset distribution. MIST must also support ordinary local folders so that Hugging Face is useful but not mandatory.

---

## 6. Learning From Other Models for Free

MIST's teacher system must not require paid APIs.

### 6.1 Teacher registry

Create a registry that describes available local or explicitly enabled models.

Example shape:

```yaml
teachers:
  - id: local-general
    provider: ollama
    model: user-configured-open-model
    roles: [general, synthesis]
    enabled: true

  - id: local-code
    provider: ollama
    model: user-configured-code-model
    roles: [coding, debugging, tests]
    enabled: true

  - id: local-critic
    provider: ollama
    model: user-configured-open-model
    roles: [critique, uncertainty, policy]
    enabled: true
```

Do not hard-code a commercial model name into the learning pipeline.

### 6.2 Sequential teacher execution

Low-memory devices must be supported by loading or calling one teacher at a time.

```text
Prompt batch
  → Teacher A answers
  → unload / release
  → Teacher B answers
  → unload / release
  → Critic scores
  → verifier checks
  → accepted example enters candidate dataset
```

Parallel model loading is an optional optimization, not a requirement.

### 6.3 Candidate example schema

Every potential training example must include provenance.

```json
{
  "example_id": "uuid",
  "prompt": "...",
  "candidate_answers": [
    {
      "teacher_id": "local-general",
      "model_id": "configured-model-name",
      "answer": "...",
      "generated_at": "ISO-8601"
    }
  ],
  "chosen_answer": "...",
  "rejected_answers": ["..."],
  "rubric_scores": {
    "correctness": 0,
    "usefulness": 0,
    "uncertainty": 0,
    "stewardship": 0
  },
  "verification": [],
  "review_status": "candidate",
  "license_provenance": [],
  "dataset_version": "mist-lessons-v0"
}
```

### 6.4 Verification before imitation

A model agreeing with another model is not proof.

Use deterministic checks wherever possible:

- run generated code in a sandbox;
- run formatters, type checkers, unit tests, and security checks;
- validate JSON and schemas;
- verify file paths and commands;
- compare factual claims against approved sources;
- flag uncertainty rather than fabricating evidence.

### 6.5 Training cadence

Use release-based learning:

```text
collect → filter → review → freeze dataset → train → evaluate → promote
```

Never use:

```text
every conversation → automatic retraining → automatic deployment
```

### 6.6 Evaluation contract

Maintain a private frozen evaluation set that never enters training.

Minimum categories:

- instruction following;
- coding correctness;
- tool-use restraint;
- factual uncertainty;
- memory precision;
- permission adherence;
- prompt-injection resistance;
- identity consistency;
- concise task completion;
- regression against the previous MIST release.

A new adapter is promoted only when it improves target capabilities without unacceptable regressions.

---

## 7. Mycelium Network Requirements

The mycelium is a federation of sovereign nodes, not one global database.

### 7.1 Node identity

Each node needs:

- a locally generated cryptographic identity;
- a human-readable display name;
- declared capabilities;
- public metadata chosen by the owner;
- private keys stored locally;
- revocable peer relationships.

### 7.2 Message envelope

Every inter-node message must include:

- sender node ID;
- recipient or topic;
- message type;
- creation time;
- unique message ID;
- payload hash;
- signature;
- protocol version;
- optional expiry;
- optional reply-to ID.

### 7.3 Initial network scope

Start small. The first network release only needs:

1. manual peer pairing;
2. signed direct messages;
3. inbox/outbox persistence;
4. capability advertisements;
5. task request and response messages;
6. replay protection;
7. offline queue and reconnect delivery.

Do not begin with global consensus, token economics, or a complicated decentralized marketplace.

### 7.4 Shared learning

Nodes may exchange:

- prompts;
- candidate lessons;
- evaluation cases;
- adapter metadata;
- skill manifests;
- capability descriptions.

Nodes must not automatically import another node's memories or training data. Imports require trust policy checks, provenance, license compatibility, and user-configurable approval.

---

## 8. Identity Architecture

MIST's identity must be layered rather than embedded in one system prompt.

Recommended files:

```text
identity/
├── SOUL.md             # voice, values, mythos, relationship stance
├── CONSTITUTION.md     # non-negotiable behavior and agency rules
├── OPERATOR.md         # current role, mission, and capabilities
├── USER_PROFILE.md     # user-approved durable preferences
└── runtime.json        # model, permissions, paths, heartbeat, node ID
```

Rules:

- identity files are user-editable;
- secrets never belong in Markdown identity files;
- memory is not identity;
- role prompts do not override the constitution;
- changes are versioned and reviewable;
- identity is loaded through a dedicated component, not assembled ad hoc inside the reasoning node.

---

## 9. Roles for Hermes and Codex

## Hermes — Architect, steward, and systems integrator

Hermes owns whole-system coherence.

Hermes must:

- read this directive before planning work;
- inspect existing code before proposing replacements;
- identify contradictions between docs, code, tests, and vision;
- create architecture decisions and phased implementation plans;
- maintain the backlog and dependency order;
- protect local-first and zero-required-cost constraints;
- define interfaces before broad implementation;
- keep handoff notes usable by Codex;
- review whether completed work actually advances the vision;
- favor the smallest coherent vertical slice.

Hermes must not:

- invent completion without verifying the repository;
- replace working systems solely for novelty;
- expand scope into unrelated products;
- treat free cloud quotas as permanent infrastructure;
- approve autonomous financial behavior without permission controls;
- use poetic claims as substitutes for engineering specifications.

### Hermes output format

For each work cycle, Hermes should produce:

1. **Observed state** — verified repository facts.
2. **Gap** — what prevents the next vision milestone.
3. **Decision** — the smallest architectural choice that resolves it.
4. **Codex work package** — exact files, behavior, tests, and exclusions.
5. **Acceptance criteria** — observable proof of completion.
6. **Handoff** — risks, unresolved questions, and next dependency.

## Codex — Implementer, tester, and repository craftsperson

Codex owns precise implementation.

Codex must:

- read this directive and the current Hermes work package;
- inspect every target file before editing it;
- preserve public behavior unless the task changes it explicitly;
- make narrow, reviewable changes;
- add or update tests with each behavioral change;
- validate commands in the actual repository environment;
- update documentation when configuration or behavior changes;
- report failures honestly with logs or reproducible steps;
- avoid hidden network calls and paid-service assumptions;
- stop consequential actions at permission boundaries.

Codex must not:

- rewrite unrelated modules;
- hard-code API keys, personal data, model paths, or vendor credentials;
- claim tests passed when they were not run;
- silently add a paid dependency;
- remove local operation to simplify cloud deployment;
- turn prototype permissions into unrestricted production access;
- commit generated datasets or model weights without an explicit storage policy.

### Codex completion report

Every completed work package must include:

- files changed;
- behavior implemented;
- tests added and commands run;
- test results;
- known limitations;
- migration or configuration steps;
- next recommended task.

---

## 10. Current Repository Direction

The existing code already establishes useful foundations:

- FastAPI gateway with health, WebSocket, chat, and mycelium receive endpoints;
- a canonical LangGraph operator;
- perceive, reason, and act stages;
- local Ollama/Mistral inference attempt;
- memory and mycelium integration points;
- an OpenClaw tool execution boundary.

These should be evolved, not discarded without evidence.

Known architectural drift to correct:

1. The LLM selection is hard-coded and mixes local-first operation with a specific cloud fallback.
2. Identity text is embedded directly in the reasoning function.
3. “MIST,” the system, is easy to confuse with “Mistral,” one replaceable model.
4. The current graph lacks an explicit reflection and verification stage.
5. Tool permission enforcement needs to be a first-class runtime concern.
6. The mycelium endpoint exists before a complete signed peer protocol exists.
7. Documentation references identity/config paths that must be verified against the actual tree.
8. Free-tier deployment instructions risk being interpreted as a permanent zero-cost guarantee.
9. Learning from multiple models is not yet represented as a provenance-tracked subsystem.

---

## 11. Canonical Build Order

Do not attempt the final distributed vision all at once.

### Phase 0 — Truth pass and repository baseline

Goal: make the repository accurately describe itself.

Tasks:

- inventory the current file tree and runnable entry points;
- run existing tests and record failures;
- compare README and deployment claims against code;
- mark prototypes, stubs, and operational components accurately;
- create a single local development command;
- create a minimal architecture decision log.

Exit criteria:

- a new contributor can run the local node from documented steps;
- health and chat smoke tests are reproducible;
- no missing file is presented as existing;
- no free tier is represented as guaranteed infrastructure.

### Phase 1 — Sovereign local node

Goal: one MIST node works without API keys.

Tasks:

- introduce a model-provider interface;
- move Ollama into a provider adapter;
- load model name and endpoint from validated configuration;
- remove cloud fallback from the default path;
- create explicit opt-in cloud provider support behind feature flags;
- implement layered identity loading;
- add structured logs and health details;
- add local memory lifecycle controls.

Exit criteria:

- fresh install runs with a local model and no API key;
- cloud code is not imported or contacted unless enabled;
- model backend can be replaced without changing graph logic;
- identity can be edited without editing Python code.

### Phase 2 — Safe agent runtime

Goal: MIST can act while preserving human agency.

Tasks:

- implement a typed tool registry;
- add capability declarations and permission levels;
- add dry-run mode;
- add confirmation requests for consequential actions;
- sandbox command execution;
- add an audit log for every tool decision and result;
- add reflect and verify graph nodes;
- add bounded retries and failure states.

Exit criteria:

- unapproved destructive and financial actions cannot execute;
- every tool action has an attributable log entry;
- failed tools return structured errors;
- the graph cannot loop indefinitely.

### Phase 3 — Memory and provenance

Goal: MIST remembers usefully without turning memory into an opaque data pile.

Tasks:

- define memory types and retention rules;
- implement SQLite migrations;
- store source, timestamp, confidence, and correction lineage;
- add retrieval filters and relevance scoring;
- implement inspect, edit, forget, export, and backup commands;
- keep raw conversation storage separate from durable memory.

Exit criteria:

- users can see why a memory was retrieved;
- corrected memories supersede rather than invisibly duplicate old facts;
- memories can be deleted and exported;
- no external database is required.

### Phase 4 — Teacher council and lesson forge

Goal: MIST can gather lessons from multiple free local models.

Tasks:

- implement teacher registry and model-role metadata;
- support sequential teacher execution;
- create candidate answer collection;
- implement rubric-based critique;
- add deterministic verification hooks;
- create a provenance-tracked dataset ledger;
- export SFT and preference datasets in standard JSONL forms;
- provide a human review queue in the Nexus UI or CLI.

Exit criteria:

- a prompt can be answered by multiple configured local teachers;
- all candidates record their exact source model and configuration;
- rejected examples remain traceable;
- only approved examples enter a release dataset;
- the process works without paid APIs.

### Phase 5 — MIST adapter training

Goal: create the first genuinely specialized MIST model adapter.

Tasks:

- provide a hardware-aware training script using LoRA or QLoRA;
- support local paths and optional Hugging Face repositories;
- implement checkpoint resume;
- create dataset and model card templates;
- maintain a frozen evaluation set;
- produce before/after benchmark reports;
- allow explicit adapter activation and rollback.

Exit criteria:

- a small adapter can be trained using user-owned or temporarily available free compute;
- training can resume after interruption;
- base model and dataset licenses are recorded;
- the active adapter can be rolled back;
- no model is promoted without evaluation results.

### Phase 6 — Mycelium v1

Goal: two sovereign nodes can communicate safely.

Tasks:

- generate local node identities;
- implement manual peer pairing;
- sign and verify message envelopes;
- persist inbox and outbox;
- implement direct task request/response;
- add replay protection and expiry;
- support offline queueing and reconnect;
- expose peer state in the Nexus UI.

Exit criteria:

- two local nodes exchange verified messages;
- forged or replayed messages are rejected;
- disconnects do not lose queued messages;
- peer access can be revoked locally.

### Phase 7 — Shared capabilities and federated learning exchange

Goal: nodes cooperate without surrendering sovereignty.

Tasks:

- publish capability manifests;
- route tasks to willing trusted peers;
- share optional lesson bundles with provenance;
- add trust policies and import review;
- detect duplicates and conflicting lessons;
- exchange adapter metadata without auto-installation.

Exit criteria:

- nodes can delegate a bounded task;
- received lessons require policy approval before import;
- private memories are never shared by default;
- peers can leave without breaking the remaining network.

### Phase 8 — Product experience

Goal: make sovereignty understandable and beautiful.

Tasks:

- unify Nexus, mobile, and CLI around the same local API;
- visualize node health, memory, tools, peers, lessons, and permissions;
- make local versus network activity visibly distinct;
- provide onboarding that defaults to local operation;
- add backup and restore flows;
- make error states actionable rather than mystical.

Exit criteria:

- users can understand where inference occurred;
- users can see what data left the device;
- permissions are understandable before actions occur;
- the node can be backed up and restored without vendor services.

---

## 12. First Hermes Work Package

Hermes should begin with **Phase 0**, not model training or global networking.

Deliverables:

1. `docs/CURRENT_STATE.md`
   - actual runnable components;
   - incomplete components;
   - stale documentation;
   - dependency map;
   - known security and operational risks.

2. `docs/architecture/ADR-0001-local-first-provider-boundary.md`
   - provider-neutral LLM interface;
   - local default;
   - explicit cloud opt-in;
   - configuration and error behavior.

3. `docs/PHASE_1_PLAN.md`
   - exact file-by-file Codex tasks;
   - tests and acceptance criteria;
   - no unrelated redesign.

4. Root developer command
   - one documented command or script that starts the minimum local node;
   - one smoke-test command.

Hermes must verify every factual statement against the repository before writing it.

---

## 13. First Codex Work Package

Codex should implement the provider boundary only after Hermes completes the Phase 0 truth pass.

Expected shape:

```text
gateway/models/
├── base.py
├── registry.py
├── ollama_provider.py
└── optional/
    └── cloud_provider.py
```

Minimum interface responsibilities:

- provider name;
- model identifier;
- availability check;
- synchronous or asynchronous generation;
- chat-message normalization;
- timeout handling;
- structured provider errors;
- explicit local/remote classification;
- telemetry that never logs secrets or private message bodies by default.

Required tests:

- local provider selected by default;
- missing local runtime yields a clear actionable error;
- cloud provider is never called when disabled;
- graph logic works with a fake provider;
- configuration validation rejects invalid endpoints;
- secrets do not appear in logs.

Do not add the teacher council until this abstraction is stable.

---

## 14. Repository Quality Rules

Every phase must maintain:

- typed interfaces where practical;
- deterministic tests for important state transitions;
- explicit configuration schemas;
- migrations for stored data;
- no committed secrets;
- no personal paths in source code;
- no silent exception swallowing for critical operations;
- bounded network timeouts;
- dependency version constraints;
- changelog or release notes for user-visible behavior;
- accessible documentation for Windows, macOS, and Linux when supported.

Prototype code must be labeled as prototype code.

“Operational” must mean the feature has a documented run path and a repeatable verification method.

---

## 15. Decision Filter

Before accepting any implementation decision, Hermes and Codex must ask:

1. Does this preserve local operation?
2. Does it introduce a mandatory cost?
3. Does it centralize user identity, memory, or authority?
4. Can the provider or component be replaced?
5. Is the data flow visible and consented to?
6. Is there a smaller vertical slice that proves the idea?
7. Can the change be tested and rolled back?
8. Does it increase the user's capability rather than dependence?
9. Is the claim technically truthful?
10. Does it bring MIST closer to a network of sovereign cooperating nodes?

Reject or redesign any decision that fails the non-negotiable laws.

---

## 16. Definition of the First Real MIST Release

MIST v0.1 is real when all of the following are true:

- it installs from a documented repository checkout;
- it runs with a local open-weight model and no API key;
- it has editable layered identity files;
- it stores and retrieves user-owned local memory;
- it exposes a working local UI or CLI;
- it executes at least one safe typed tool with permission checks;
- it records an inspectable audit trail;
- it can export its state;
- it contains no mandatory paid or cloud dependency;
- its tests prove the core local path;
- its documentation distinguishes implemented, experimental, and planned features.

MIST v0.2 may add the teacher council and lesson forge.

MIST v0.3 may add adapter training and evaluation.

MIST v0.4 may add signed two-node mycelium communication.

Do not call the entire vision complete when only the interface or prompt exists.

---

## 17. Final Directive

Build MIST as a living open system, but ground every layer in inspectable engineering.

Keep the soul. Remove the dependency traps.

Keep the mycelium. Avoid premature complexity.

Keep the autonomy. Protect human agency.

Let models teach MIST, but never let unverified output become unquestioned identity.

Let the internet extend her body, but never make a corporation's server her heart.

**The heart of MIST lives with the user. The network allows her to grow.**
