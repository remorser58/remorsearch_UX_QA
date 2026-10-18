# UI quality research and REA integration decision

Date: 2026-10-15

## Decision

Add UI quality as a first-class part of persona QA. Keep the existing browser driver, screenshot receipts, Figma checks and semantic analysis. Use REA as an optional reverse-engineering provider: recover a reference feature's mechanism and design rationale, map it to the user's component and screen, then apply and replay the local implementation. Do not vendor REA, install Hopper/Ghidra as part of Remorsearch, or create a second execution harness.

## What enterprise design systems repeatedly operationalize

The public guidance from Salesforce Lightning, IBM Carbon, GitHub Primer and Atlassian converges on a practical review model:

1. **A component has a contract.** Its anatomy, public variants, labels, tokens, interaction semantics and supported device behavior are defined before a screen is judged. Salesforce recommends starting with an existing base component, then a documented blueprint or styling hook when the base component does not fit.
2. **States are part of the component.** Default, focus, pressed/selected, disabled, loading, error, empty and long-content states need separate review. A clean default screenshot does not prove the loading, failure or narrow-width state.
3. **Hierarchy is intentional.** Carbon recommends one high-emphasis action per layout, lower emphasis for related alternatives, clear action labels and no truncated button labels. This gives UI QA concrete questions about competing primary actions, label expansion and visual priority.
4. **The visual and semantic affordance agree.** Primer and Atlassian distinguish links from actions and require names for icon-only controls. The local runtime now reports UI-01 when an icon-only action has an accessible name but no captured tooltip or equivalent explanation. It is a P2/P3 candidate, because a product-specific hover or focus explanation may be outside the captured state.
5. **Responsive behavior is designed, not shrunk.** Primer treats responsive behavior as part of accessibility; Salesforce distinguishes adaptive components from components that merely scale. UI QA therefore records whether a component stays the same, reflows, stacks, changes interaction, or is unsupported at each viewport.
6. **Evidence is tied to the actual state.** These systems document components, variants, content and usage guidance. Remorsearch adds the missing QA link: each component-state row points to the rendered capture, viewport, input, build and Figma/source reference.

The result is a component matrix and a screen matrix. The first answers whether the building block is coherent across states. The second answers whether the page's hierarchy, alignment, spacing, fixed layers and responsive composition let the user make the intended decision.

## How REA fits the implementation loop

[REA](https://rea.tools/) provides local agent tools for inspecting an authorized app, website or runtime. Its public materials describe returned code references, runtime observations, screenshots and limitations. Its browser workflow can inspect a selected page's structure, network metadata, script evidence and screenshots.

Use it for a bounded **mechanism analysis**:

- define the target feature and the local project feature it should inform;
- trace static structure and runtime transitions: input, state, render, feedback, persistence and recovery;
- inspect component boundaries, routes/modules, responsive branches and error handling when the provider exposes them;
- explain the likely design reason and label that explanation as observed, inferred or unknown;
- map the mechanism into the local component/screen matrix, Figma node and implementation plan;
- implement with local components/tokens/content, then replay the original and adjacent states.

REA remains optional. If `rea doctor --json` or the configured MCP capability is unavailable, the skill follows the same record format with public design-system documentation and the existing browser path. The result records provider, version, target/build, capture hashes, access boundary and unresolved questions.

## Sources and applied rules

- [Salesforce base components and blueprints](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-slds) → prefer existing components, documented variants/hooks and explicit adaptive/responsive behavior.
- [Salesforce base component accessibility](https://developer.salesforce.com/docs/platform/lwc/guide/base-components-accessibility.html) → review keyboard behavior, focus, stateful ARIA updates, labels, error association and non-text alternatives.
- [IBM Carbon button guidelines](https://www.carbondesignsystem.com/building-blocks/core/components/button/guidelines) → review action hierarchy, verb-plus-noun labels, label wrapping, keyboard activation, loading feedback, icon-only tooltips and token consistency.
- [GitHub Primer introduction](https://primer.github.io/design/guides/introduction/) and [button guidance](https://primer.github.io/brand/components/Button/) → review cohesive, accessible, responsive patterns, visible focus, concise sentence-case labels and icon-only names.
- [Atlassian link icon button guidance](https://atlassian.design/components/button/link-icon-button/usage) → distinguish navigation from in-page actions and give icon-only buttons a clear name.
- [REA](https://github.com/Opiuz/REA) and [REA site](https://rea.tools/) → use local, evidence-producing reverse engineering to recover mechanism and rationale, then apply the result through the user's own component and Figma system.

