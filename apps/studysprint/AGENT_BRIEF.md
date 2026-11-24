# StudySprint — mobile exploratory QA brief

Read the tester provider's AGENT_BRIEF.md first. Its tools, safety rules, and final-report contract apply in full. You are testing the StudySprint Android app as one assigned persona. Use only synthetic study content and the isolated emulator data. Dispatch this Android-only app with ios_personas=none.

## Product map

StudySprint is a study and spaced-repetition app. Its Android shell loads the bundled web app. The primary surfaces are Today, Plan, Reviews, and Reader.

## Mission

Evaluate whether a learner can understand the current study state, move between the four surfaces, complete a small study action, and return without losing state.

1. Inspect Today. Identify the next study action and whether the current state is understandable.
2. Open Plan. Check schedule clarity, empty/loading states, and navigation back to Today.
3. Open Reviews. Use only synthetic content already present or create a clearly synthetic item if the UI supports it. Check whether a review action gives visible feedback.
4. Open Reader. Check text hierarchy, scrolling, reading comfort, and navigation back to the other surfaces.
5. Background/resume or relaunch the app once where safe; verify state remains coherent.
6. Inspect keyboard behavior, tap-target reachability, contrast, truncation, and accessibility names.

## Evidence rules

- Capture a screenshot after every meaningful action.
- Report reproducible steps, actual versus expected result, screen name, severity, and screenshot numbers.
- Distinguish an app defect from a missing feature, unsupported locale, test-environment failure, or persona expectation.
- Mark uncertain observations as uncertain.
- Preserve each persona's independent finding; duplicate grouping is only a hypothesis.
- Use no real email, personal account, real learner data, or external service account.
- Do not alter device settings outside the assigned persona profile.
- Do not clear app data, uninstall, or change production state.

## StudySprint-specific checks

- Verify the app leaves its initial loading state and displays a non-empty surface version.
- Verify Today, Plan, Reviews, and Reader are reachable and each returns to a stable state.
- Check that long text and large font sizes remain readable and actionable.
- Check that dark mode maintains readable contrast.
- Check Reader content for clipping and scroll behavior.
- Report unsupported languages as coverage gaps, not confirmed translation defects.

## Final output

Follow the provider AGENT_BRIEF.md output contract exactly. Write results/<persona>/report.md and results/<persona>/findings.json using the assigned PERSONA ID. The JSON object includes score and an issues array; each issue includes title, severity (blocker, major, minor, or cosmetic), and screen, with optional screenshots. Save screenshots and raw evidence under results/<persona>/ so the provider workflow includes them in its encrypted result bundle.
