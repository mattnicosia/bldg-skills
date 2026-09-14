# Delta card template

Copy this into `DELTA.md` for every run.

```markdown
# Capability delta

Site:
Incumbent:
Challenger:
Date:
Evidence tier used (1–5):

| Axis | Incumbent | Challenger | Delta | Evidence (one line) | Site now | Decision |
|---|---|---|---|---|---|---|
| Hierarchy | | | up/same/down/unproven | | hold/gap/broken | allow / hold / probe |
| Type | | | | | | |
| Color and material | | | | | | |
| Motion | | | | | | |
| Page coherence | | | | | | |
| Vision self-check | | | | | | |
| Constraint respect | | | | | | |
| Copy and tone | | | | | | |
| Interaction / states | | | | | | |
| 3D / shaders | | | | | | |
| A11y and contrast | | | | | | |
| Front-end correctness | | | | | | |

Allow list (max 3)
- ...

Hold list (do not touch)
- ...

Probe list (tiny, reversible)
- ...
```

Decision rule

- allow = gap/broken AND challenger up
- hold = site already strong OR challenger down/same
- probe = challenger unproven AND the risk is contained to one component
