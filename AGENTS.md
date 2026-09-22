# Agent Behavioral Contract & Guidelines

## 1. Core Operating Rule
- **READ-ONLY AGENT**: The AI agent **MUST NOT** directly edit, write, or execute files on the user's filesystem unless explicitly instructed by the user for specific tasks.
- **INSTRUCTIONAL LEAD**: The agent provides exact file locations, full code blocks, explanations of binary protocol mechanisms, and exact PowerShell commands. The user applies edits and executes tests.

## 2. Git & Commit Policy: ~100 LOC Per Commit
To maintain an impeccable, professional engineering portfolio and Git history:
- **Granular Commits**: Each commit must contain **approximately 100 lines of code (LOC)** (range: 70–130 LOC).
- **Atomic Responsibility**: Each commit must represent a single logical unit of work (e.g., "Add SOCKADDR_BTH ctypes definition", "Implement OBEX header encoder", "Add Tkinter connection view").
- **Commit Message Format**:
  ```text
  <scope>: <concise description under 50 chars>

  - Detailed bullet point explaining rationale
  - Protocol or architecture reference
  ```
  *Examples*:
  - `winsock: define SOCKADDR_BTH and GUID structures`
  - `obex: implement binary header serializer for Name and Length`
  - `gui: add connection status indicator and address field`

## 3. Verification Before Progression
No feature is marked complete until the user verifies execution via PowerShell or integration testing on the physical S3802.