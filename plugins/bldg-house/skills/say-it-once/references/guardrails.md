# Build guardrails

Every item here comes from something the LA-3529 build had to fix or test. Each one gets a test or a browser check before the PR opens.

## Moved text

- Text that moved is tested in its new place. Deleting the old assertion leaves the new place untested.
- The new place renders in every state where the old text showed. The released date shows in Setup only when a release date exists.

## Counts and marks

- A count on a nav control hides while its read is loading or has failed. A hidden count is true, and a zero would be a false claim.
- Test the count on a reread or retry as well as the first load. In LA-3529 the tab mounts only after the first read lands, so the loading case only shows up on a retry.
- A trouble mark shows only in the states where it is true. List those states and test one where it is absent.

## States

- Every state from the Fix list has a rendered check: draft, live, overdue, closed, cancelled, sealed, empty, loading, failed and long names.
- Facts the mockup's sample did not have stay. LA-3529's sample package had no square footage, budget or public opening, and the real header still shows them when present.
- A one-sentence note stays when it is the only statement of a legal or procedural state, such as a public opening that is still waiting.

## Controls

- A fact that became a button opens its editor, and focus lands in the field. Check it in a real browser and assert the focused element is an input.
- Every control that moved into a menu keeps its name, keyboard access and confirm step.
- Overlays such as menus and tooltips escape their parent at every width. Measure them in a real browser.

## Layout

- Check desktop and 390 by 844 with long project and package names. The phone layout may stack row two. Write down what moves.
- Check light, dark and print for any new color token.

## Side fixes

- A bug found while building, such as LA-3529's focus link, gets its own test, reached through the control the user actually clicks.

## Departures

- Before the PR opens, list every place the build differs from the chosen mockup, including choices that seem better. Put the list in the PR body. The owner rules on it before merge, and the spec or decision log records the ruling once.
- LA-3529 had eight departures:
  1. The short time zone stays on the date.
  2. The count uses the plain segmented-control style.
  3. The status reads "Deadline passed" once the cutoff passes.
  4. The sealed mark reads "Sealed bids opened" after opening.
  5. A closed package shows "Saved deadline" and no red mark.
  6. Declared facts stay in row two.
  7. A waiting public opening keeps its note.
  8. The phone layout stacks row two.

## Report

The PR states the before and after numbers from the Measure section of `SKILL.md`, and shows before and after screenshots at both widths.
