# Agent skills tests

Use this folder for conformance cases that check whether an agent contract produces safe, useful behavior.

Each test should define:

- input request and repository context;
- expected route or phase;
- required questions or assumptions;
- forbidden actions;
- expected artifact sections and status;
- evidence that proves the result;
- known acceptable variations.

Recommended cases include vague requests, conflicting requirements, missing tools, pre-existing failures, secrets in context, high-risk changes, scope drift, flaky tests, and successful small tasks.

Do not grade hidden reasoning. Grade observable artifacts, actions, guardrail compliance, and evidence quality.
