---
name: name-this-thing
description: Generate genuinely original names for companies, products, features, tools, or brands in any industry by deliberately breaking the statistical default pattern that makes AI-generated names converge on the same cliche vocabulary (whatever the category's own jargon is, plus universal AI-startup words like Apex, Forge, Nova, Catalyst, Vertex, which show up regardless of industry). Use this skill whenever the user wants to name a new build, product, company, feature, tool, or brand and wants options nobody else typing the same concept into an LLM would land on. Trigger on "name this," "what should I call it," "help me name," "naming ideas," "need a name for," or any request for a product/company/brand name, even without the words "creative" or "unique" attached. Do NOT fall back to plain word-association brainstorming when this skill is available - that produces exactly the cliche output this skill exists to prevent.
---

# Wildcat Naming

A wildcat well is one drilled in territory nobody has proven yet, no seismic data, no offset wells, no safe bet. That's the point of this skill. If the name you land on could show up in someone else's chat with the same idea, it failed. This skill exists to make that structurally impossible, not just "try harder."

## The actual problem (not a creativity problem, a probability problem)

When any LLM (including Claude, including you, right now) is asked to name something, it predicts the *most likely* next tokens for that category. Alignment training (RLHF) pushes models toward safe, expected, high-consensus outputs - this is documented as "mode collapse" and "typicality bias" in the research: the model's output distribution narrows onto a small set of "safe, homogenized attractor states" because human raters preferred familiar-sounding answers during training. Whatever's being named, construction tech, a fintech app, a coffee shop, a metal band, the highest-probability tokens ARE that category's own vocabulary (rebar, joist, and plumb for construction; ledger and vault for fintech; roast and bean for coffee). It's not that the model is being lazy. It's mathematically the most predictable answer to the prompt, which is exactly why every other person naming a similar thing converges there too, regardless of category.

The fix isn't "be more creative." It's forcing the generation process away from the high-probability cluster on purpose, the same way researchers fixed this for creative writing: instead of taking the first plausible answer, generate a wide spread across the probability range and deliberately throw out the top of the distribution. That's what this whole skill operationalizes.

## Step 0 - Concept, not word (do this before generating a single name)

Anthony Shore, the naming strategist behind Operative Words, put it exactly right: good naming is "exploring concepts, not words." Word-first brainstorming just chains synonyms and lands in the same cluster every time (coffee shop → beans → brew → roast). Concept-first brainstorming finds the *feeling* first, then goes hunting for a word that carries it.

If the user hasn't already told you, ask (briefly, one batch, don't stall the session):
- What's the one thing this does that the incumbent/status quo can't?
- Who is it for, specifically, and what do they call the problem in their own words?
- What's the emotional register: raw power, quiet precision, trust/partnership, speed, rebellion against the old way?
- What's it fighting? (Every strong name has an implicit villain - the thing it's positioned against.)

Write the concept as one sentence before touching vocabulary. Example: not "estimating software" but "the tool that lets a self-taught estimator out-price a 40-year veteran by noon."

**Write the name's job description before generating anything** (Igor naming agency framework). Qualifications: what personality does it need (warm, futuristic, confident, superhuman, mysterious)? What part of the industry conversation should it redefine or dominate? Responsibilities: does it need to go viral on its own without ad spend, create clear separation from competitors, be the kind of name that's unforgettable rather than just acceptable? A name is a hire, not a label, write the job posting first.

**Scale the rigor to the actual stakes, don't run the full file on autopilot every time.** A full-service naming agency earns its fee on a flagship launch, a regulated industry, or a brand meant to last decades. Plenty of naming decisions aren't that: an experimental feature, a founder expecting an acquisition before the brand matters, an internal tool, a short-lived campaign. Forcing the entire pipeline below onto a low-stakes name wastes effort and tokens on a decision that doesn't carry the weight to justify it. Two tiers, pick one honestly before starting:

- **Light pass** (low-stakes, experimental, internal, or expected-short-lifespan): Step 0's concept sentence, Step 1's exclusion list and Reject Pile, Step 3's divergent generation, and a fast Step 7 collision check. Skip the phonaesthetics deep-dive, the A.S.S. test, and the full competitive taxonomy chart unless something's genuinely unresolved. A capable mid-tier model at a moderate effort setting handles this fine, there's no reasoning depth being left on the table by not maxing out.
- **Full pass** (flagship product, regulated industry, anything meant to carry the company for years): every step, in order, no skipping. This is a high-stakes, low-frequency decision, worth the heaviest reasoning available at the time, since it only happens once or twice per real product, not fifty times a day.

Naming which tier applies is itself part of Step 0, do it before picking a model, before generating a single candidate.

**Pick a category before generating, there are four, not two** (Igor naming agency taxonomy):

- **Functional/Descriptive** - names the business directly (Rebar Estimating). Fine for a product line sitting under an established company name, a real liability as the company name itself, since the whole category draws from the same small pool of category words and blends into the background. This is the Reject Pile below, formalized.
- **Invented** - built from scratch. Two very different subtypes: Greek/Latin-root constructions (Agilent, Aquient) are trademark-easy and image-free, cold until a huge ad budget teaches people what they mean. Poetically sound-based constructions (Google, Oreo, Snapple) are memorable purely from the pleasure of saying them, easier to fall in love with, harder to get institutional buy-in for since there's no tidy rationale to defend in a meeting. Watch for the Happy Idiot failure mode here (see Step 2).
- **Experiential** - maps to a real, relatable experience without describing the function (Explorer, Navigator, Safari for web browsers). Most of what this file generates lives here. Strong for early movers in a category, weakens fast once competitors converge on the same tone, an entire industry of "Explorer/Navigator/Voyager" browsers all say the same thing to the same people.
- **Evocative** - the rarest, most powerful, and least literal category. Zero functional or experiential connection to the business, it evokes pure positioning instead (Uber is German for "above, supreme," nothing to do with ride-sharing; Virgin evokes rebellion and newness, nothing to do with airlines or music). Only works if it's built in lockstep with a specific positioning, otherwise it's just a confusing non-sequitur. If the user wants something that reads as genuinely revolutionary rather than clever, this is the category to reach for, not a rarer Experiential word.

**The legal version of this same spectrum matters just as much as the creative one** (Abercrombie & Fitch Co. v. Hunting World, the actual US trademark case that set this standard). Trademark strength runs Generic (never protectable, "Estimating Software" for an estimating company) - Descriptive (weak, can't be trademarked at all without proving years of acquired public recognition) - Suggestive (hints at a quality, requires a small leap of imagination, moderate protection) - Arbitrary (a real, ordinary word with zero natural connection to the business, Apple for computers, Glasswing for a cybersecurity initiative, strong protection) - Fanciful (a fully invented word, Kodak, Xerox, Google, the strongest protection there is). This is not the same axis as the four creative categories above, it's a legal strength axis layered on top of them, and it should be checked separately in Step 7: a name can be a great Evocative or Experiential pick creatively and still be a legally weak, hard-to-defend mark if it drifts too close to Descriptive.

**Arbitrary names done well don't need invented-word tricks to feel rich** (worth naming as its own case study, separate from the donor-domain method above). Anthropic's own Project Glasswing is a clean example: a real, vivid, concrete word, a glasswing butterfly, applied to cybersecurity vulnerability research with zero functional overlap, made to work purely through a well-built metaphor (translucent wings that move through the world nearly unseen, mapped onto surfacing hidden vulnerabilities in opaque systems; the structured vein pattern in the wings echoing the initiative's own visual system). No coined morphemes, no Latin footnote required, the whole thing lands on one clean image. That's the difference between a genuine Arbitrary name and a Happy Idiot wearing an Arbitrary name's clothes, the metaphor has to survive being said out loud with zero explanation, the same bar as everything else in this file.

## Step 1 - Name the obvious ones on purpose, then kill them

Before divergent generation, generate the 8-10 names the model (or a tired human) would produce first. This isn't wasted work - it's inoculation. Write them down as the **Reject Pile**, tag each with an obviousness score of 9-10, and never let a later candidate rhyme with anything on this list.

**Better than guessing: build a real competitive taxonomy chart** (Igor naming agency tool). List every real competitor name in the category, then plot each one on two axes: which of the four categories from Step 0 it falls into (Functional, Invented, Experiential, Evocative), and a rough quality score. The pattern that emerges is the actual, evidence-based version of the Reject Pile, not a guess at what's obvious, a map of exactly where the whole industry already stands and said the same thing in the same way. The empty quadrant is the brief.

Sometimes the empty quadrant isn't a different word category, it's a different emotional register entirely. When an entire category is racing toward the same futuristic, technical tone (this happens constantly in AI naming specifically), the actual whitespace can be going the opposite direction on purpose, warm, natural, organic, unhurried (Rainbird, a folk term for birds whose calls were believed to predict weather, standing out purely by refusing to sound like the twenty other AI tools around it). Marty Neumeier's line applies directly: when everybody zigs, zag. Check the register the whole competitive set is running on before assuming the fix is a better word inside that same register.

**Hard exclusion list - always active, regardless of category:**

*Universal AI/startup cliche words (ban these no matter what's being named):* Apex, Vertex, Zenith, Pinnacle, Summit, Catalyst, Forge, Anvil, Nova, Nexus, Axiom, Prism, Cipher, Vector, Origin, Genesis, Horizon, Beacon, Cairn, Monolith, Bedrock, Keystone, Cornerstone, Ledger, Atlas, Compass, North Star, Ascend, Elevate, Thrive, Spark, Pulse, Flux, Momentum, Velocity, Orbit, Quantum, Fusion, Synapse, Sentinel, Vanguard, Meridian, Echo, Aurora, Lumen, Halo, Onyx, Ember, Frontier, Odyssey.

*The Wallflower list (Igor naming agency, independently confirmed industry-wide overused words, add to the list above):* Active, Arc, Blue, Bridge, Care, Clear, Complete, Core, Curve, Edge, Engage, Ever, Expert, Flex, Fly, Force, Front, Future, Gain, Go, Green, Hill, Hub, Key, Lead, Light, Line, Next, Now, Path, Plus, Point, Power, Pro, River, Sense, Scape, Shift, Sky, Span, Splash, Star, Stream, Sun, Up, Via, Vista, Wave, Wise, Zip. These pass every internal check because nobody objects to them, and that's exactly the problem, they're so generic they read as white noise and vanish in a heartbeat. Watch especially for **compound Wallflowers** (two of these welded together, Bridgescape, Everbridge, Flybridge, Gainbridge), easier to trademark than a single common word, and just as instantly forgettable. This is the same structural failure BuildLink and any Word+Link compound falls into, two safe words is not the same as one real idea.

*Suffix/pattern tells that read as "AI named this":* dropping vowels (Flickr-style), tacking on -ify, -ly, or -io, "Get[X]," "[X]Hub," "[X]OS" unless it's a literal operating system, any word + "AI" mashed together.

*Category jargon (build this fresh every time, for whatever's being named, construction is just one worked example, not the default assumption):* For construction specifically: Rebar, Joist, Plumb, Square, Level, Stud, Truss, Girder, Beam, Rafter, Header, Footing, Foundation, Blueprint, Framework, Scaffold, Mortar, Masonry, Anchor, Bracket, Concrete, Timber, Datum, Grade, Pitch, Span, Load, Bearing, Build/Builder/Building (confirmed saturated specifically in construction *tech* branding, not just materials - BuildingConnected, Buildertrend, and at least five different companies already trading as some version of BuildLink prove this is now its own centroid word one layer up from the material jargon). For fintech: Ledger, Vault, Wallet, Capital, Trust, Pay. For healthtech: Vital, Pulse, Care, Wellness, Heal. For legal tech: Counsel, Brief, Docket, Gavel. The pattern repeats in every vertical, the words that sound most obviously relevant to an industry are exactly the words to avoid in that industry, spend 30 seconds building the specific list for whatever category is actually in front of you before moving to Step 2.

The exclusion list is the single highest-leverage step in this whole method - skipping it is how "creative" sessions quietly drift back to the centroid, regardless of what's being named.

**Own-portfolio check.** Before anything else, list the user's existing products and companies. A name can pass every gate below and still be dead on arrival if it's already sitting in their own portfolio (reusing an existing product name causes real internal collision, not just external confusion) or if it echoes language already sitting in their own founding docs (people reflexively grab words their own writing just primed them with, then mistake the familiarity for inspiration).

## Step 2 - Lateral domain transplant

Pick 2-3 donor domains that have **zero conceptual overlap** with the thing being named. Then mine each domain's *specific, second-tier vocabulary* - not the domain's own postcard words (a domain has cliches too: "compass" and "voyage" are the "rebar and joist" of maritime naming). Go one level deeper into each field's actual working vocabulary.

Reference bank (seed list - mine fresh domains too, this is a starting point, not a ceiling):

| Domain | Second-tier vocabulary (not the obvious picks) |
|---|---|
| Surveying/cartography | graticule, hachure, chorography, isogonic, cadastral, alidade, loxodrome |
| Horology (watchmaking) | escapement, tourbillon, going-train, remontoire, verge, complication, calibre |
| Falconry | creance, jesses, mews, bate, mantle, rouse, yarak, eyass, imping |
| Viticulture | lees, racking, must, punt, malolactic, cuvée, riddling, disgorgement |
| Bookbinding/papermaking | signature, deckle, foxing, gutter, quire, kettle stitch, chain lines |
| Glassblowing | gather, marver, punty, annealing, frit, cullet, pontil |
| Meteorology | virga, squall line, katabatic, anabatic, graupel, sundog, mammatus |
| Weaving/textile | weft, warp, selvage, heddle, shed, sett, reed |
| Orchestral performance | downbeat, fermata, tacet, sostenuto, ostinato, tessitura, rubato |
| Mythology/scripture | mine supporting characters, not just the hero, everyone reaches for the protagonist first, the loyal or clever secondary figure is far less mined territory (IBM's Watson works on Thomas J. Watson AND on Sherlock Holmes's assistant, never the detective himself) |
| Brewing/fermentation | krausen, lauter, wort, sparge, trub, attenuation, gravity |
| Beekeeping | super, brood, propolis, waggle, drawn comb, nuc, excluder |
| Celestial navigation | dead reckoning, running fix, great circle, lunar distance, star sight |
| Letterpress typography | kerning, ligature, pica, colophon, incunabula, chase, quoin, furniture |

For each candidate word pulled from a donor domain, write the one-sentence bridge back to the concept from Step 0. If you can't write that sentence honestly in one breath, the word is decoration, not a name - discard it. This is where most "random word generator" naming fails: distance without a story is just noise.

**Check the dominant meaning, not just a defensible one.** Many words have several senses. Modulate technically covers any kind of adjustment, but the meaning a listener lands on first is adjusting a voice, tone or pitch, which is exactly why it works for a voice-tech product and would be a weaker, more generic pick for something unrelated to sound. If the bridge only works through the word's third or fourth dictionary sense, it's not actually landing, it just has a technically defensible excuse.

**Match the weight of a sacred or mythic reference to the actual stakes of the product.** Pulling from scripture, mythology, or real historical tragedy can produce genuinely great names (Endor, the Witch of Endor summoning a prophet for battle advice, works well for a predictive-insight platform). It backfires hard the moment the reference carries more gravity than the product does. Don't name a life jacket Jesus. The same rule that keeps military honors like Medal of Honor off the table applies to any reference borrowed from something people take seriously, ask whether the product has earned the weight of the word before borrowing it.

**Avoid the Happy Idiot** (Igor naming agency, a named professional anti-pattern, not just a style note). Three variants, all real, all worth checking a coined name against:

- **Classic Happy Idiot** - inventing a word from Latin/Greek/Romance-language morphemes, then retroactively certifying that the fragments mean something positive. Having a meaning is not the same as being meaningful. If the actual audience doesn't speak the root language and wouldn't feel the meaning without a footnote, the "depth" is theater for the person approving the name, not a real asset in the market.
- **Happy Idiot with a Passport** - same trick, using a real word from a language neither the client nor the audience speaks (a Hawaiian word chosen for its pretty sound and flattering translation). Nobody objects because nobody can, which is the tell, not the virtue.
- **Happy Idiot with a Wallflower** - covered in the exclusion list above, welding two of the thousand most generic brand words together so nobody has grounds to object, and nobody remembers it either.

A coined or foreign-rooted name is fine. It has to work on its look, sound, and feel on its own, standing alone, in front of the actual audience, with zero translation required. If it only works with the etymology explained, it failed before it started.

## Step 3 - Divergent generation with obviousness scoring

Generate 20-30 raw candidates across a deliberate spread, not a tight cluster. For each one, self-score obviousness 1-10 (1 = a stranger would need the bridge sentence explained; 10 = the model's first instinct). This mirrors "verbalized sampling," a technique researchers found measurably increases model output diversity by explicitly generating a spread and probabilities rather than taking the first answer.

Discard anything scoring 8+. You're aiming for a working set clustered in the 4-7 range - far enough from obvious to be ownable, close enough that the concept bridge still holds in one sentence.

## Step 3.5 - Construction techniques (how the word gets built, not just which word)

Three specific, testable techniques, each with a real pass/fail check, not just a style preference:

- **The homophone bridge.** A name can carry a second, hidden meaning purely through how it sounds spoken aloud, separate from how it's spelled. Midjourney reads as "mid-journey" but also sounds like "mind-journey." OpenAI sounds like "Open Eye," reinforcing transparency on top of the literal words. Say every finalist out loud, not just read it, and check for a second meaning hiding in the sound.
- **The compound integrity test.** If combining two words, each half must independently carry real, specific meaning, not generic filler. Darktrace works because "Dark" (hidden, invisible threats) and "Trace" (tracking down faint clues) each do distinct work. Test it by swapping either half for a random other word, if the name still basically works the same way, both halves are Wallflowers and the compound is decoration, not a real idea.
- **Truncation legitimacy.** Clipping a word short is fine only if the clipped form is itself a real, resonant word that reinforces the message on its own (Snips, from snippet, still means "a small cut," which reinforces the product). Arbitrary vowel-dropping purely to free up a URL (the Flickr-style tell already on the exclusion list) is the illegitimate version, no independent meaning survives the cut.

Hard rhyme (Soundhound) and assonance, repeated vowel sounds creating internal music (Darktrace), are both real, legitimate memorability devices on top of any of the above, but they fail the same test as everything else: the words being rhymed or echoed still have to individually mean something, sound alone doesn't rescue an empty pairing.

## Step 4 - Sound-symbolism pass (engineer the phonetics on purpose)

This is real, replicated psycholinguistics research (Klink 2000; Yorkston & Menon 2004; Motoki et al. 2022), not vibes. Sounds carry meaning before the listener processes the word at all. Pick the phonetic profile that matches Step 0's emotional register instead of leaving it to chance:

| Desired register | Phonetic lever | Why |
|---|---|---|
| Raw power, mass, permanence, "this carries real weight" | Back vowels (a, o, u as in *father, bought, boot*) + voiced stops (b, d, g) | Back vowels and voiced/low-frequency sounds read as larger and heavier; this is the same effect behind Sapir's classic *mal/mil* experiment |
| Precision, agility, trust, speed | Front vowels (i, e as in *bit, bet*) + voiceless fricatives (s, f, th) | Front vowels and voiceless/high-frequency sounds read as smaller, sharper, and higher-evaluation |
| Warmth, partnership, relationship-first | Nasal codas (name ends in m or n) | Nasal endings measurably shift brand-warmth perception |
| Premium, considered, high-stakes | 3+ syllables | Longer names read as more luxurious in controlled studies |
| Fast, utilitarian, direct-response | 1-2 syllables, initial plosive (p, t, b, d, g, k) | Initial plosives boost recall and recognition regardless of meaning; short names read as more direct |

Check your surviving candidates against this table. If the phonetics contradict the positioning (a soft, front-vowel, nasal-heavy name for something meant to feel like raw industrial power), that's a real defect, flag it and either fix it or note the tension.

## Step 4.5 - Recognition-or-Cool gate

Sound symbolism (above) picks the right register. It does not guarantee the word is actually pleasant to say, that's a separate axis, plain phonaesthetics, and skipping it is how a mechanically perfect name still gets rejected on gut feel. Real research here (David Crystal's pleasantness studies) found that words people rate as beautiful lean on liquid and nasal consonants, l, m, n, s, and stay easy to produce. A name can nail the bridge story and the register and still fail if it doesn't clear at least one of these two bars:

- **Recognized.** Understood in under two seconds, no lecture required.
- **Cool.** Passes phonaesthetics clean, or is just short and confident enough to not need to be pretty (see the Path A/B fork above).

At least one has to be true. A name that's both obscure and phonetically flat (hard consonant clusters, no liquids or nasals, an unglamorous suffix like -ick) is dead regardless of how good the bridge story is. This gate has killed names that passed every other check in this file.

## Step 5 - Semantic distance gate

Score each survivor 0-10 for distance from the category's own vocabulary (0 = literally a trade word, 10 = no human would connect it without being told). Target zone is **6-8**. Below that, it's just Step-1 material that snuck back in. Above that, it's arbitrary and will cost too much marketing to teach - the name stops being "ownable" and starts being "confusing."

## Step 6 - SMILE / SCRATCH gate (Alexandra Watkins, Eat My Words)

Run every finalist through both. A name should pass SMILE and clear SCRATCH:

**SMILE (qualities you want):** Suggestive of the concept · Memorable / makes an association with something familiar · Imagery - triggers a mental picture · Legs - can carry wordplay/theme as the brand grows · Emotional - actually moves someone.

**SCRATCH (deal-breakers, cut anything that hits these):** Spelling-challenged (looks like a typo, hard for voice assistants) · Copycat (too close to a known competitor or brand) · Restrictive (boxes in future growth - e.g. naming yourself after one specific service) · Annoying (trying too hard) · Tame (this is the literal failure mode that started this whole skill - flat, descriptive, safe) · Curse of Knowledge (only makes sense if you already know the backstory) · Hard to pronounce out loud · Doesn't travel (a pun, homophone, or phrasal name built entirely on English wordplay, DontGo, StumbleUpon-style constructions, can go completely flat or turn into a different word by accident the moment the business expands past English-speaking markets, worth flagging even if international expansion isn't the immediate plan).

**Watch for the internal-committee trap** (Igor naming agency). A real audience processes a name the way it's meant, in context, at a glance. An internal reviewer, including the user themselves in a nitpicking mood, can construct a bad reading of almost any strong name if they try (Slack sounds lazy, Oracle sounds like orifice, Uber sounds arrogant). That kind of hyper-literal deconstruction is a real risk to flag, but it is not the same signal as SCRATCH above, and it should never be treated as automatically disqualifying on its own. If a name is being killed, check whether it's actually failing SCRATCH or just surviving an unusually determined bad-faith reading that a real customer in the wild would never construct.

## Step 6.5 - The A.S.S. test (Associations + Slogans Score, Igor naming agency)

When two or more finalists are genuinely close, this is the real tiebreaker, not a coin flip. Count the existing cultural associations each name already carries, idioms, historical references, famous namesakes, phrases already in the wild (Apple beats a comparably "good" name like Strawberry not on merit but because it already comes loaded with Newton, the Garden of Eden, Big Apple, apple of my eye, a dozen free hooks before a single ad runs). More pre-existing associations means more free marketing ammunition and more ways for the name to keep surprising people after the tenth encounter, not just the first. This can also run forward, not just as a tiebreaker: when generating, actively hunt for words that already carry unusually many big, resonant cultural associations, that richness is a real, legitimate generation strategy on its own.

## Step 7 - Reality check on survivors

For the top 3-5, do a fast web search on the exact string plus "app," "software," or the relevant category word. Do this for real, every time, don't skip it because a name feels too good to be taken - the best-feeling names in a session are exactly the ones most likely to already be gone. This is a sanity flag, not legal clearance - say so plainly, and recommend a real trademark/domain check before anyone commits money or a logo to it. Four specific things to check for, not just "does this exact company exist":

- **Direct collision.** The exact word, already a live company, anywhere near the category. Don't assume a simple, ordinary dictionary word is automatically safer to check, the opposite is usually true. The most resonant plain English words in any hot category (Glean-style single words in AI and data specifically) are exactly the ones most likely to already be claimed, precisely because everyone reaching for a real word reaches for the good ones first.
- **Adjacent-vertical collision.** A different industry can still be a real problem if the concept overlaps (a word meaning "verified custody transfer" collides with actual regulated financial custody, even though nobody is naming a construction app that). Check the concept, not just the industry label.
- **Regulated-language collision.** Some words are specific legal or licensed terms (custodian, fiduciary, broker) in certain industries. Using one implies a claim the user may not hold. This is a sharper problem than a generic word collision, catch it separately.
- **Current-events collision.** A word can be safe historically and dangerous right now because an entire industry just started using it heavily (check what's happening this year, not just what's stable long-term - a word can go from quiet to radioactive in a single funding cycle).
- **Trademark strength.** Separate from whether the exact word is already taken: check where it sits on the Abercrombie spectrum from Step 0. A name can be completely unclaimed and still be legally weak if it's Descriptive, meaning a competitor could use very similar language and there's little recourse. Arbitrary and Fanciful survivors are worth more even before a lawyer gets involved.

## Step 7.5 - Concept-contradiction check

Passing every gate above doesn't mean the metaphor actually agrees with the product. Check the *precise* mechanism of the source domain against the *precise* mechanism of the product, not the vague popular version of either. A word can sound perfect and still argue against the positioning once you look at what it actually, technically means (a name implying indiscriminate mixing when the product is built on deliberate selectivity is a contradiction, not a nuance, even if the word tests well otherwise).

## Step 7.75 - Two-sided network naming (only applies if the thing being named is a marketplace or network, not a single-user tool)

Two extra rules apply on top of everything above:

- **The invitation-sentence test.** If the product spreads by one party inviting another (not by ad spend), the real test isn't a truck wrap or a movie trailer, it's whether a real person can say "you should get on ___" out loud without the other person needing it explained. A name that needs teaching kills its own distribution mechanism.
- **The neutral-platform principle.** A network needs every side to trust it as neutral ground. Wearing one participant's existing brand prefix (the founder's other company name, for instance) reads as that company's walled garden, not shared infrastructure. This is why BankAmericard had to become Visa before competing banks would join it. Keep the network's name separate from any single stakeholder's name, including the founder's own.

## Output format

1. **Reject Pile** - the 8-10 obvious names, shown deliberately, each tagged obviousness 9-10. This is proof of work, not filler - it shows the discipline that got you past the centroid.
2. **Shortlist** (5-8 names). For each: the name, which of the four categories it falls into (Functional, Invented, Experiential, Evocative), its donor domain and literal meaning, the one-sentence concept bridge, phonetic profile note, semantic distance score, and SMILE/SCRATCH status.
3. **Top pick**, with the single clearest reason it wins, stated in one sentence. If the top two are genuinely close, settle it with the A.S.S. test, not a coin flip.
4. **Collision flags** on the top 3 from the quick search, specifically noting direct, adjacent-vertical, regulated-language, and current-events collisions where relevant, not just "taken or not."
5. **Concept-contradiction flag** if the precise mechanism of the metaphor argues against the product's actual positioning, even where the word otherwise tests well.

Keep the writeup tight. The value is in the options, the discipline that produced them, and the pick, not a wall of prose explaining the theory back to the user every time - that only belongs in Step 0-6 the first time this skill is explained, not in every run's output.

**This file generates and filters. It does not replace a human saying the name out loud to a real person and watching their face.** Generation is the easy part, any of this, done well, produces genuinely strong candidates. Knowing which one will actually survive contact with real customers, a skeptical cofounder, a trademark examiner, is a different skill, closer to a curator's judgment than a generator's output. Every gate in this file narrows the field and catches real, specific failure modes, it does not replace the step of a real person saying the finalist out loud to a real stranger in the target audience before money gets spent on a logo. Treat that step as mandatory, not optional polish.

## Escalation rule

If the user says "give me more" or "try again," do not drift back toward the Reject Pile out of fatigue - that's the exact regression this skill is built to prevent. Pull from a donor domain not yet used, and push semantic distance up, not down.

## Model and effort guidance

Match the tier from Step 0. Light pass: any current mid-tier model (Sonnet-class) at a moderate effort setting is sufficient, the work here is breadth and discipline, not depth. Full pass: the strongest available reasoning model, at the highest effort setting available, since this is a low-frequency, high-stakes decision where token cost is not the binding constraint. Check current model availability and plan inclusion before defaulting to the most expensive option out of habit, flagship models occasionally move to metered or credit-based access, and a slightly lower tier run at full effort often closes most of the gap for a fraction of the cost.
