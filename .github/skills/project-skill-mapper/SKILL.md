---
name: project-skill-mapper
description: 'Identify which skills a software project needs. Use when asked: which skills need this project, what skills should we create, or how to map repo modules to reusable skill workflows.'
argument-hint: 'Project context or specific area to evaluate (backend, frontend, AI model, testing, docs, DevOps)'
---

# Project Skill Mapper

## What This Skill Produces
A prioritized list of recommended skills for the current project, each with:
- Purpose and scope
- Why the project needs it
- Expected inputs and outputs
- Priority (P1, P2, P3)
- Suggested primitive (`SKILL.md`, prompt, instruction, or agent)

Also generates starter `SKILL.md` files for top-priority recommendations when requested.

## When to Use
- User asks which skills are needed for a project.
- Team wants to convert repeated workflows into reusable skills.
- You need a gap analysis between project complexity and existing automation.

## Required Inputs
- Repository structure and major components
- Current pain points (if provided)
- Team goals (speed, quality, reliability, modernization)

If goals are missing, proceed with repository evidence and state assumptions.

## Procedure
1. Inventory project domains
- Identify major technical areas (for example: AI/ML, backend API, frontend app, tests, docs, deployment).
- Note folders, frameworks, and integration boundaries.

2. Detect repeated workflows
- Find tasks likely to repeat across sprints (for example: endpoint additions, schema updates, validation pipeline updates, test updates, release checks).
- Prefer workflows with clear steps and recurring decision points.

3. Convert workflows to candidate skills
- Create one candidate skill per reusable workflow.
- Keep each skill narrow enough to be invoked on demand.

4. Apply decision logic for customization type
- Use a skill when the workflow is multi-step and repeatable.
- Use a prompt when it is a single focused transformation.
- Use instructions when behavior should always apply.
- Use a custom agent only if stage isolation or tool constraints are required.

5. Score and prioritize
- Assign P1 to high-frequency, high-risk workflows.
- Assign P2 to medium-frequency workflows or quality boosters.
- Assign P3 to occasional or convenience workflows.

6. Produce recommendation table
- Output: skill name, trigger phrases, owner area, priority, and short rationale.

7. Generate starter skills for top priorities
- Select top 1-3 P1 items.
- Create one folder per skill under `.github/skills/<skill-name>/`.
- Add a minimal but valid `SKILL.md` with strong `description` trigger phrases.
- Ensure each skill has a clear outcome, procedure, and completion criteria.

## Decision Points
- If the user wants personal reuse across projects: place in personal scope.
- If the workflow is project-specific: place in workspace scope.
- If the user only wants a checklist: output a compact checklist version.
- If the user wants team automation: output full workflow with quality gates.

## Quality Checks
Before finalizing recommendations, verify:
- Every major project domain is covered.
- No candidate is too broad or duplicates another candidate.
- Trigger phrases in descriptions are specific and discoverable.
- The final list is prioritized and actionable.

## Output Format
Use this structure:

1. Recommended Skills (Prioritized)
- `skill-name` | Priority | Domain | Why needed | Suggested customization type

2. Suggested First Skill to Build
- Name
- Scope (workspace or personal)
- Minimal outcome for v1

3. Risks or Gaps
- Missing information that could change recommendations
- Assumptions made during analysis

## Completion Criteria
This skill is complete only when:
- Recommendations are prioritized
- Each recommendation includes a concrete rationale
- Scope decision (workspace vs personal) is explicit
- At least one starter skill is identified for immediate implementation
- Starter `SKILL.md` files are created for selected P1 items when generation is requested
