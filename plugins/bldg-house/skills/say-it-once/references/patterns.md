# Patterns

Each pattern has a tell (how to spot it), a fix, and the risk to check first. The LA-3529 instance follows each one.

## 1. One fact, two places

**Tell.** The same status, date, name or count appears twice in one area: a chip and a heading, a breadcrumb and a title, a summary card and the row below it.

**Fix.** Keep the mention where the user acts on it and delete the rest.

**Risk.** The two mentions can differ slightly, as "Out to bid" and "Bidding stays open until you close it" did. Check the second one is not the only place a real distinction lives.

**LA-3529.** The status showed as a chip and again as the readiness card's heading. The released date showed in the header and again inside the card. The title closed the breadcrumb and then showed as the heading.

## 2. A sentence that restates a chip

**Tell.** A full sentence beside a chip, badge or label that already carries its meaning. Sentences in headers, cards and toolbars are almost always this.

**Fix.** Delete the sentence. If it adds a real fact, turn that fact into a token on the chip or a short mark ("14d past").

**Risk.** Some sentences are warnings about a consequence, such as "Saving changes does not email bidders." Those move beside the action they warn about. They stay on the screen.

**LA-3529.** "Bidding stays open until you close it" sat under an "Out to bid" chip, which already said the package took bids.

## 3. A button that only switches a view

**Tell.** A button or card link whose handler sets the active tab, scrolls, or navigates to a place the nav already reaches.

**Fix.** Delete it, or put the information it was pointing at onto the nav control itself, such as a count on the tab.

**Risk.** Check it was not the only route to a deep section on phone, where tabs can be hidden.

**LA-3529.** The readiness card's "Request details" and "Track Bids" buttons only switched to tabs that sat a row below. Track Bids now carries the bid count.

## 4. A rare action in a prime spot

**Tell.** A top-row button that people use weekly or less, sitting beside the actions they use every visit.

**Fix.** Move it into an overflow menu (···) in the same area. Keep destructive actions in the menu too, behind their existing confirm step.

**Risk.** Discoverability. Name the menu item exactly as the old button, and keep keyboard access.

**LA-3529.** Focus moved from the header row into the ··· menu, beside Review and award, Follow-up rules and Cancel.

## 5. Too much precision for the glance

**Tell.** The full year on a date this year, a long time zone name such as "(America/New_York)", seconds, full addresses, IDs.

**Fix.** Show the short form and put the full value in a tooltip and the accessible label.

**Risk.** A project rule may require part of it to show. VERIDEX requires a deadline to show its time zone, so the build kept "EDT" and moved only the long name to the tooltip. That was a departure from the mockup and went to the owner.

## 6. Context in the wrong place

**Tell.** A note or fact that only matters while editing something, shown on a read-only summary.

**Fix.** Move it to the editor where it applies.

**LA-3529.** "Released Oct 2" and "Saving changes does not email bidders" moved from the header to Setup, beside the bid date and its Save button.

## 7. The fact is the control

**Tell.** A value with a separate edit button or a "change" link elsewhere.

**Fix.** Make the value itself the button. It opens the editor with the cursor already in the field.

**Risk.** Check the focus lands on a focusable element. The LA-3529 build found an older "Change bid date" link that focused a form, which cannot take focus, so the cursor went nowhere.

## 8. A sign of trouble that does not stand out

**Tell.** An overdue, failed or blocked state shown in the same ink as normal text, or only in a sentence.

**Fix.** A short colored mark ("14d past") in the danger color, next to the value it describes.

**Risk.** Add the color as a token with dark-mode and print values, and check contrast on every background the mark can sit on. Show it only in the states where it is true: a closed or cancelled package shows no overdue mark.

## 9. Wordy labels

**Tell.** Labels with words that add nothing: "Add new bidder", "Click here to", "Manage your".

**Fix.** Cut to verb and object: "Add Bidder". Follow the project's label case rule.

## 10. A tall stack of bands

**Tell.** Breadcrumb, title, status, card and tabs each on their own band, with gaps between them.

**Fix.** Merge them into one card of two rows. Row one says what this is and its state. Row two holds the view switch and the one or two actions used every visit.

**LA-3529.** Five rows became two. Row one is the project link, title, status and ··· menu. Row two is Setup and Track Bids, the bid date, and Add Bidder.

## 11. The same sentence on every row

**Tell.** A list where each row ends with the same instruction or explanation. `scripts/repeat_scan.py` reports it under repeated sentences, with a count equal to the number of rows.

**Fix.** State it once, as the section's subtitle or as the row's action label, and keep only what differs per row.

**Risk.** Check the sentence really is identical. A row that says something different has to keep its own text.

**VERIDEX Overview, found by the first scan.** Each of five overdue rows ends with "Review the request and decide whether to close bidding or move the bid date," under a section already titled Overdue Packages.

## Where a removed element goes

| The element is | Its destination |
|---|---|
| Already said elsewhere in the area | Delete it |
| A warning about a consequence | Beside the action it warns about |
| A fact needed only while editing | The editor for that fact |
| An action used weekly or less | The overflow menu |
| Precision a glance does not need | Tooltip and accessible label, unless a rule requires it visible |
| A pointer to another view | A count or mark on that view's nav control |
| The same instruction on every row | Once, as the section subtitle or the row's action label |
| A required fact | Keeps a visible home. Never only a tooltip |

## The LA-3529 ladder

- **A, one line of facts.** The card goes, its sentence moves onto the status pill, the date drops the year and long zone, and rare actions go to the ··· menu.
- **B, the deadline leads.** The date gets its own block with one next step that changes with the state.
- **C, header and tabs in one band.** Name, status, date and view switch in one card of two rows.
- **D, two rows, no sentences** (chosen). C with every sentence removed. The date is a button that opens the bid date, a red mark says how far past it is, and Track Bids carries its bid count.
