# UI quality and reference analysis

Use this card by section for every product UI QA, including task-focused checks. Pure research skips it. It extends task, recovery, keyboard and accessibility checks with direct visual inspection.

## Host visual procedure

Execute with existing image, browser and Figma tools; add no harness or dependencies.

1. Bind the actual URL/current build or source revision, state, viewport/DPR and scroll position to its capture. Bind the reference to its Figma file/branch/version/node/readback and export. Inspect the exact source and current build used by the capture; a stale screenshot cannot establish their state. Missing source identity limits fidelity, not actual-screen inspection.
2. Open **both actual and reference pixels** with `view_image` for local files, or browser/Figma tools that return images the host can inspect. Capture/export success, paths, DOM dumps and analyzer counts do not mean the images were viewed. View the unlabelled original first. For long images, inspect an overview, then overlapping top/middle/bottom and relevant component regions at readable scale; do not judge tiny fit-to-screen text. Retain original artifact IDs and each crop's origin, scale and coordinates so observations map back to source pixels.
3. Match component role, variant and state even when copy or frame dimensions differ. Compare local alignment, type roles, spacing relationships and wrapping constraints; state content/dimension differences. Exact `pixel_diff` requires matching state, content and viewport/DPR; verify font/asset readiness and record differences. Use the existing comparator and contract when eligible; unmatched frames get component-level review, never a fabricated exact diff. Color difference measures changed pixels, not good design; matching a defective Figma frame can still reproduce a defect.
4. Inspect each category below separately. Check browser computed styles and loaded fonts, text/line bounds, container padding/gaps and Figma text bounds/font/resize settings. Trace clipping through every relevant ancestor: overflow, line clamp, masks, transforms and stacking. Confirm candidates against real pixels. Fixed height or intersecting boxes alone do not prove failure. A normal viewport cutoff is not content loss: scroll/reveal and check whether required content remains readable/reachable. Prove lost text or blocked controls in the actual state before grading it.
5. Validate spacing/hierarchy against repeated local components, tokens, stated intent or an approved design rule. Different content can legitimately change height and gaps; taste alone creates no defect. Inspect Figma itself for clipping, overlap and inconsistent rules. Classify implementation defect, design defect, spec conflict or approved deviation; keep reference fidelity separate from usability.
6. Write region observations and actual/reference **viewed artifact IDs** using `references/loop/provider-contract.md` section 3 and its current schema. Map the review categories to supported provider aspects; do not invent keys or IDs. Each observation needs region/coordinate space, exact visible text or control, expected rule, observed pixels, supporting geometry/source evidence and pass/fail/unknown with reason. Include failures and unknowns; no passed-only records without observations. Missing/unviewed reference leaves fidelity unknown. Preserve originals and link crops; annotations are aids, never proof that the original was viewed.

| Review category | Evidence to inspect and record |
| --- | --- |
| alignment | Component edges/baselines and container/grid rule; quote the affected labels and coordinates. |
| spacing | Measured padding/gap against a repeated local instance/token/intent; account for wrapped copy and component roles. |
| typography | Actual loaded font, size/weight/line height, text/line bounds and visible wrapping against the reference role. Korean lines must not split a word or start with `·` or closing punctuation; check each engine and width. |
| clipping | Exact missing glyph/line, text bounds, clipping ancestor chain and pixels after scroll/reveal; map to `text_clipping`. |
| occlusion | Covering layer/stack, affected text/control and pixels; check opacity, hit testing and reachability; map to `component_occlusion`. |
| figma_fidelity | Matching node/version/state and viewed actual/reference regions; record source defects and approved deviations separately. |

For forward tests, use neutral task instructions and view the unlabelled original plus a clean control before consulting annotations or prior findings. Record both outcomes. Do not teach the skill named-page defects or assume the control is clean without inspecting it.

## What mature product teams check

Treat a component as a small public system, not a screenshot. Inspect the component and the screen that composes it.

| Area | Inspect | Evidence required |
| --- | --- | --- |
| System | token roles for type, color, spacing, radius, elevation and motion; repeated values; component API/variants | source token or Figma readback, plus the rendered instance |
| Anatomy | label, icon, container, helper/error text, affordance and hit area | screenshot and DOM/a11y snapshot for the same state |
| State matrix | default, hover where applicable, focus, pressed, selected, disabled, loading, error, empty and long content | reached states with viewport and input recorded; unreached states stay untested |
| Hierarchy | one clear primary action, lower-emphasis alternatives, action versus navigation semantics, destructive separation | screen capture and task step that establishes the decision |
| Content | action labels, sentence case or local writing convention, long Korean/English strings, plural and currency formatting | exact visible text, source/spec, long-content capture |
| Responsive | narrow width, short height, mobile adaptation, safe-area/fixed bars, table/list/card changes | same component at each scoped viewport and engine |
| Text geometry | text bounds wider than the parent content box, fixed-height text parents, `nowrap`, hidden/clip overflow, or a wrapped line colliding with the next block | Figma readback or DOM geometry plus the painted screenshot; record `text_clipping` separately from general layout |
| Layer geometry | a component, overlay, sticky/fixed layer or transparent hit target covers required text or a control | same-state painted screenshot, layer/stack evidence and task consequence; record `component_occlusion` separately |
| Interaction | focus indicator, tooltip for icon-only controls, keyboard activation, loading feedback, error association, focus return | action trace, capture before/after, accessibility fields; screen-reader speech remains separate |

Do not turn a design-system recommendation into a defect automatically. A finding needs a task consequence, a stated product intent, a Figma/spec conflict, or a directly verified component rule. Keep taste, brand preference and untested states in the annex.

## Component and screen matrix

Create one row per meaningful component instance, not per DOM wrapper:

```json
{
  "component_key": "checkout.primary-action",
  "primitive": "button",
  "variant": "primary",
  "state": "loading",
  "screen": "checkout",
  "viewport": "320x568 CSS px",
  "input": "touch",
  "source": "Figma node or public design-system URL",
  "capture": "captures/checkout-loading.png",
  "status": "pass | fail | untested",
  "reason": "exact observation or missing state"
}
```

For screens, record all six review categories with region observations and viewed artifact IDs, plus hierarchy, fixed-layer/responsive behavior and the primary decision. A screenshot count is not coverage. A screen passes only when every required state/viewport has passing observed results; keep text-clipping and component-occlusion results separate. The matrix illustrates review notes, not a replacement provider schema.

## REA reverse-engineering pass

REA means [Reverse Engineer Anything](https://rea.tools/). Use it to recover how an authorized app, website or runtime works: code references, module and route relationships, component boundaries, runtime transitions, screenshots and unresolved questions. The goal is to explain the mechanism and the design reason, then rebuild that behavior in the user's project with its own Figma, tokens and components.

Use REA when it is already installed or the user explicitly authorizes setup. The Remorsearch package does not vendor REA or add another execution runtime. Detect it first (`rea doctor --json` or the configured MCP capability); if unavailable, use the same investigation record with public design-system documentation and the existing browser path.

For each feature or screen:

1. Define the user decision, target state, allowed target and the local project feature that should benefit from the investigation.
2. Inspect the target's static structure and runtime behavior where the provider supports it: entry point, modules/routes, component boundaries, state variables, event handlers, network or storage relationships, responsive branches, error and recovery transitions.
3. Replay the important states and record the causal chain: input → state change → render/update → feedback → persistence or recovery. Mark every item `observed`, `inferred` or `unknown`.
4. Explain why the reference likely uses the pattern: task priority, error prevention, information hierarchy, latency, responsive constraint, accessibility or maintainability. Keep this as a hypothesis until the evidence supports it.
5. Create a local transfer record: reference mechanism, local component/screen, Figma node, adaptation, implementation path, trade-off, replay state and acceptance evidence. Apply the change through the project's design source (Figma first when design lives there) and the loop workflow, then rerun the original and adjacent states.

Inspect only the feature slice needed to answer the question. Record the target URL/build, REA version/provider, evidence hashes, access boundary and unresolved questions. Transfer the mechanism and rationale; use the user's project components, tokens, assets and content for implementation.

## Reference principles used by this card

- [Salesforce Lightning base components and blueprints](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-slds): use an existing base component or documented blueprint, expose a stable public shape, use documented variants/hooks and account for adaptive versus responsive support.
- [Salesforce component accessibility](https://developer.salesforce.com/docs/platform/lwc/guide/base-components-accessibility.html): keyboard behavior, focus, ARIA state updates, labels, error association and non-text alternatives belong in the component contract.
- [IBM Carbon button guidance](https://www.carbondesignsystem.com/building-blocks/core/components/button/guidelines): establish action hierarchy, use clear verb-plus-noun labels, do not truncate labels, provide keyboard activation/loading feedback, and explain icon-only buttons with tooltips.
- [GitHub Primer introduction](https://primer.github.io/design/guides/introduction/): cohesive, accessible and responsive behavior is considered from the start and supported by reusable patterns and tokens.
- [GitHub Primer button guidance](https://primer.github.io/brand/components/Button/): keep labels concise, preserve visible focus, use sentence case and use accessible names for icon-only buttons.
- [Atlassian link icon button guidance](https://atlassian.design/components/button/link-icon-button/usage): distinguish URL-changing links from on-page actions and give icon-only buttons a clear name.

These references are comparison material, not a universal visual style. Record the local product's approved Figma and intent before applying any principle.

