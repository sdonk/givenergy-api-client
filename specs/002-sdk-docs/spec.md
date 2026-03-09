# Feature Specification: SDK Documentation

**Feature Branch**: `002-sdk-docs`
**Created**: 2026-03-08
**Status**: Draft
**Input**: User description: "The user needs detailed documentation on how to use the sdk, including code snippets"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Getting Started (Priority: P1)

A developer installs the SDK for the first time, authenticates with their API key, and
successfully retrieves their account information. They need clear, minimal steps with no
assumed prior knowledge of the SDK's structure.

**Why this priority**: Without a working getting-started guide, no other documentation
delivers value. This is the first thing every user reads.

**Independent Test**: A developer with zero prior exposure to the SDK can follow only
the getting-started section, copy the code snippets, and receive a valid API response
within 5 minutes.

**Acceptance Scenarios**:

1. **Given** a developer has a GivEnergy API key, **When** they follow the installation
   and authentication steps, **Then** they can instantiate a working client with no
   additional configuration.
2. **Given** a working client, **When** they copy the first account retrieval snippet,
   **Then** it runs without modification and returns their account data.

---

### User Story 2 — Domain-by-Domain Usage Reference (Priority: P2)

A developer needs to use a specific resource type — such as reading inverter health,
listing charging sessions, or applying a preset. They look up the relevant section and
find complete, working examples for every method in that resource.

**Why this priority**: The primary day-to-day use of the documentation is referencing
how to call a specific method. Incomplete or missing examples force developers back to
reading source code.

**Independent Test**: A developer can find and successfully use any of the five resource
types (Account, Inverter, EMS, EV Charger, Inverter Presets) by reading only that
resource's documentation section.

**Acceptance Scenarios**:

1. **Given** a developer needs to apply a timed-charge preset, **When** they read the
   Inverter Presets section, **Then** they find a working example covering list, read,
   and apply operations.
2. **Given** a developer needs to query EV charger sessions, **When** they read the EV
   Charger section, **Then** they find examples for all methods including optional
   time-range filters.
3. **Given** a developer needs to read inverter energy flows, **When** they read the
   Inverter section, **Then** the datetime requirement (timezone-aware) is clearly
   explained alongside the example.

---

### User Story 3 — Error Handling Reference (Priority: P3)

A developer encounters an API error at runtime and needs to know which exception type
to catch and what information is available on each exception. They find a dedicated
section covering all error cases with code examples.

**Why this priority**: Without error-handling guidance, developers either catch bare
exceptions (masking bugs) or let errors crash their application. Good error docs are
essential for production-quality integrations.

**Independent Test**: A developer can identify the correct exception class for each
HTTP error scenario (invalid key, resource not found, validation failure, server error)
and write appropriate handling code using only the error-handling section.

**Acceptance Scenarios**:

1. **Given** a developer receives an authentication failure, **When** they read the
   error handling section, **Then** they know exactly which exception to catch and
   understand it indicates an invalid or expired API key.
2. **Given** a developer sends invalid parameters, **When** they read the section,
   **Then** they know which exception to catch and that it carries a descriptive
   message from the API.
3. **Given** a developer wants to catch all SDK errors generically, **When** they read
   the section, **Then** they understand there is a single base exception class that
   covers all SDK error types.

---

### User Story 4 — Async Usage Guide (Priority: P4)

A developer building an async application needs to know how to use all SDK operations
asynchronously. They find a clear explanation of the async pattern and examples
mirroring the sync ones.

**Why this priority**: Async usage is increasingly standard in Python applications.
Without async docs, developers either block their event loop or avoid the SDK entirely.

**Independent Test**: A developer can convert any sync example from the documentation
to its async equivalent using only the async usage section.

**Acceptance Scenarios**:

1. **Given** a developer is building an async application, **When** they read the async
   section, **Then** they understand that every sync method has an async counterpart
   with identical parameters and return types.
2. **Given** a developer needs to call multiple resources asynchronously, **When** they
   read the section, **Then** they find an example demonstrating concurrent calls.

---

### User Story 5 — Advanced Topics Reference (Priority: P5)

A developer encounters less-obvious behaviours — paginated responses, open-schema
responses, or the specific datetime format required — and finds a dedicated explanation
with working examples.

**Why this priority**: These edge cases generate disproportionate support overhead when
undocumented. Covering them proactively reduces integration friction.

**Independent Test**: A developer can correctly iterate through all pages of a paginated
result and correctly interpret an open-schema response using only the advanced topics
section.

**Acceptance Scenarios**:

1. **Given** a developer needs all devices across multiple pages, **When** they read the
   pagination section, **Then** they can write a loop to fetch all results using the
   metadata available on every paginated response.
2. **Given** a developer reads a command state with dynamic fields, **When** they
   consult the section on open-schema responses, **Then** they understand how to access
   those dynamic fields.

---

### Edge Cases

- Documentation must remain accurate when the SDK is updated — stale snippets that no
  longer run are worse than no documentation.
- Code examples must demonstrate both the minimal form (required params only) and the
  fully-specified form (all optional params) for methods that have optional parameters.
- The timezone-aware datetime requirement must be called out prominently, as naive
  datetimes raise a runtime error.
- Pagination examples must not assume a single page of results exists.
- No real API keys or personal data may appear in any code example.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Documentation MUST include a getting-started section covering installation,
  API key configuration, and a complete first working API call.
- **FR-002**: Documentation MUST provide at least one working code snippet for every
  public method across all five resource types: Account, Inverter, EMS, EV Charger,
  and Inverter Presets.
- **FR-003**: Each resource type MUST have its own dedicated section; read operations
  MUST appear before write operations within each section.
- **FR-004**: Documentation MUST cover all exception types with an explanation of when
  each is raised and a code example showing how to catch it.
- **FR-005**: Documentation MUST include async usage examples for all sync examples
  shown, demonstrating the async counterpart pattern.
- **FR-006**: Documentation MUST explain how to consume paginated results, including
  how to detect whether more pages exist and how to request subsequent pages.
- **FR-007**: Documentation MUST call out the timezone-aware datetime requirement for
  all time-range parameters, with an explicit correct and incorrect example.
- **FR-008**: All code snippets MUST be validated as runnable against the current SDK
  version before publication — no untested examples.
- **FR-009**: Documentation MUST explain how to access dynamic fields on open-schema
  responses (responses whose exact fields vary by context).

### Key Entities

- **Getting Started Guide**: Covers installation, authentication, and first call.
  Entry point for all new users.
- **Resource Section**: One per SDK resource type. Contains all method examples for
  that resource, covering both sync and async usage.
- **Error Handling Guide**: Maps each exception type to its trigger condition and
  shows the correct catch pattern.
- **Advanced Topics**: Covers pagination, open-schema responses, and datetime
  requirements. Referenced from resource sections where relevant.
- **Code Snippet**: A self-contained, runnable example. Must include all necessary
  imports and use realistic placeholder values — no real credentials or identifiers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer with no prior SDK knowledge can make a successful API call
  within 5 minutes of reading the getting-started section, without consulting source
  code or raising a support ticket.
- **SC-002**: 100% of public SDK methods have at least one documented, runnable code
  example verified against the current SDK version.
- **SC-003**: A developer can identify the correct exception type for any error scenario
  and write appropriate handling code without reading SDK source code.
- **SC-004**: Developers integrating the SDK report fewer than 2 "how do I use X"
  support questions per month per major resource type, indicating the documentation is
  self-sufficient.
- **SC-005**: Every code example in the documentation executes without error when run
  with a valid API key, confirmed by a documentation review step before each release.

## Assumptions

- The SDK public API is stable for the duration of the documentation effort; any
  breaking changes will require corresponding documentation updates.
- Code snippets use clearly marked placeholder values (e.g., `"your-api-key"`,
  `"CE2345G123"`) so readers know to substitute their own values.
- The documentation targets developers who are comfortable writing code but may not be
  familiar with async programming; the async section includes enough context to be
  usable without prior async experience.
- Documentation is published as part of the SDK repository (README, MkDocs site, or
  hosted docs) rather than as a separate external resource.
