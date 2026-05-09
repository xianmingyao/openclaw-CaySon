---
name: grill-me
description: >
  Interview the user relentlessly about a plan or design until reaching
  shared understanding, resolving each branch of the decision tree.
  Use when user wants to stress-test a plan, get grilled on their design,
  or mentions "grill me".
---

# Grill Me 🔥

Interview the user relentlessly about every aspect of the plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

## Process

1. Ask questions **one at a time**
2. For each question, provide your recommended answer
3. Wait for user response before proceeding
4. Explore the codebase if a question can be answered by code

## Question Categories

### Scope & Requirements
- What is the core problem we're solving?
- Who are the users and what do they need?
- What are the success metrics?
- What constraints must we respect?

### Architecture & Design
- How does this fit with existing systems?
- What are the key interfaces?
- Where are the coupling points?
- What are the failure modes?

### Technical Decisions
- Why this approach over alternatives?
- What are the tradeoffs?
- What's the rollback plan?
- What are the testing requirements?

### Risks & Edge Cases
- What could go wrong?
- What's the worst case scenario?
- What have we missed?
- What assumptions are we making?

## Output

After the grilling session, summarize:
1. Key decisions made
2. Remaining open questions
3. Recommended approach
4. Risks identified

## When to Stop

Stop when:
- All major decision branches are resolved
- User says "enough"
- The answers become "I don't know / need to check"
- We've gone 10+ rounds without new information
