---
name: visual-grounding
description: Use when the deliverable's success is VISUAL — a rendered HTML/CSS page, SVG, canvas, chart, UI component, animation, game, or any layout/styling change. The failure this kills is declaring a visual change "done" from reading the code when the rendered result is actually broken (overlap, invisible element, wrong color, offscreen, clipped, misaligned). Do not use for pure backend/logic/data code with no visual output.
---

# Visual grounding: look at the pixels, don't trust the code

Code that compiles and "reads correct" routinely renders wrong: an element is behind another, a color
resolves to transparent, flex collapses to zero height, an SVG path is offscreen, an animation never
fires. A passing build or a clean type-check verifies the *code*, not the *feature*. For anything
visual, the only real verification is **rendering it and looking at the actual output** before you
claim it works. This is the reflex a code-first model skips; make it non-optional.

## The protocol

**1. Render it.** Start the dev server / open the file in the preview (`preview_start`, or the
harness's preview tools). Never reason about appearance from the source alone.

**2. Observe the actual output — match the tool to the claim.**
- **Looks right?** → `preview_screenshot`. Look at it. Is the thing actually visible, positioned, and
  colored the way the intent requires? Squint for overlap, clipping, offscreen content, contrast.
- **Structure/content right?** → `preview_snapshot` (DOM/text) — confirm the elements exist and nest
  as intended.
- **Specific CSS value?** → `preview_inspect` computed styles — don't trust the stylesheet; read what
  actually applied after the cascade.
- **Console/network clean?** → `preview_console_logs` / `preview_network` — a silent JS error or a
  404'd asset is why the render is blank.

**3. Exercise interaction and states.** Static screenshot ≠ working feature. If it has behavior, drive
it: `preview_click` / `preview_fill` / synthetic `mousemove`, then re-snapshot to confirm the response.
For responsive or theme work, `preview_resize` and check the breakpoints / dark mode you claimed to
support — don't assume they work because the media query "looks right."

**4. Fix from what you SEE, not what the code implies.** When the render is wrong, diagnose against the
observed output and computed styles, edit the source, re-render, re-check. Loop until the pixels match
the intent — capped at a few rounds, then report the honest state.

## What reaches the user

- **Working** → show proof: a screenshot of the rendered result (or the network/console evidence for
  a non-visual fix). "It renders correctly" with the screenshot beats a paragraph asserting it does.
- **Broken and unfixable here** → say exactly what renders wrong and why, with the observed evidence —
  don't claim it works because the code "should" produce it.

## Limits

- Reading a *rendered result you produced* is grounding (do it). Reading an *image the user handed you
  to interpret* is perception — a capability axis no skill closes; prefer DOM/computed-styles/visual
  diff over raw pixels, and consider a vision-stronger model for the read (see `judgment` / the router's
  perception mode).
- If no preview/rendering path exists in this environment, say so — that's a known, stated risk the
  user inherits, not something to paper over by claiming the code looks right.
