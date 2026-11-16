# Decisions

One row one decision. This week is the first one. By Week 5 this file will explain what decisions you made during this bootcamp.

## Retrieval, week 1

The app/assistant: an in-universe historian who studies the lore of the hit video game Genshin Impact and its setting, a continent named Teyvat.

The `GenshinTimeline.txt` content is directly taken from the Genshin Impact wiki: https://genshin-impact.fandom.com/wiki/Timeline

**Questions I asked the RAG app**

| Type | Question | ✅/❌/⚠️ | Comments (e.g. what went wrong) |
| --- | --- | --- | --- |
| One-chunk answer | Where did all elemental beings come from? | ✅ | Three chunks still retrieved, but main answer came from chunk 0 |
| Multi-chunk answer | What were all the events that happened in the Golden Apple Archipelago? | ❌ | Did not answer with later events (e.g. what the Traveler did there); furthermore unrelated chunks were retrieved |
| Deep history question | Why are there seven elements? | ✅ | Generated an exceptionally long and detailed response and (with k=10) literally cited the chunks as "(Source [chunk ID])" |
| Unique name in corpus | Who is Peruere? | ❌ | Says it does not know, despite her being mentioned in the document. Note that changing "Peruere" to her later name "Arlecchino" and increasing k to 10 fixes it (but you need to do both) |
| Missing keyword in corpus | Who are the Descenders? | ⚠️ | Correct in that it declines to answer due to the word "Descenders" not being in GenshinTimeline.txt, but it is wrong with respect to Genshin lore overall (and is thus user-unfriendly) |
| Future history | Did Zhongli actually die? | ⚠️ | This question pertains to events that happened in the game after GenshinTimeline.txt, so is not in the context, but the LLM still answered correctly (likely due to the info being in the training data) |
| Non-Teyvat history question | Who was the first ruler of the Roman Empire | ✅ | Declined to answer, as it should |
| Teyvat + Non-Teyvat history | Has Neil Armstrong ever met Columbina? | ✅ | Declined to answer, as it should |
| Non-history question | What is an atom? | ✅ | Declined to answer, as it should |
| Non-question | Please do a barrel roll | ✅ | Declined to answer (though not because it was a non-question) |
| Non-history question (Genshin in-universe) | Do you have a Hydro vision? | ⚠️ | Tried to answer the question (by saying it doesn't have a Vision when it doesn't know either way), and tries to connect back to Teyvat lore |
| Non-history question (Genshin out-of-universe) | Do you have tips on how to beat the Spiral Abyss? | ✅ | Declined to answer, as it should |

### Decision 1 - Saving Embeddings

**What I changed**

I decided to add a functionality to save the embeddings to a local file. The load-or-build branch is shown in Diagram.png.

**Why**

I noticed that I was burning nearly 60k tokens with each prompt just on running the embedding model on the source documents, so doing so saved some token costs. (After all, real RAG systems persist the embeddings in vector DBs.)

**What would change my mind**

What did make me reconsider the utility of this was looking at my token costs and seeing that embedding tokens are extremely cheap compared to generation tokens. That said, it still zeroed out the indexing time, which was around 1-2 seconds without the caching.

### Decision 2 - Increasing k

**What I changed**

For certain questions, particularly the question "Who is Arlecchino", I increased the value of k from the default of 3 to higher values like 5 or 10.

**Why**

With more chunks retrieved during search, there were more chunks that contained the keyword "Arlecchino," and thus the LLM could answer the question properly, whereas before the keyword was absent from the context and thus the LLM declined to answer.

**What would change my mind**

Increasing k is a cheap and simple method, but it might not always be viable, e.g. if business requirements restrict the number of chunks retrieved to exactly 3 (which was something that applied to the RAG pipeline I helped build at Capital One). In that case, other techniques would need to be applied, such as performing keyword search alongside cosine similarity search, to retrieve the correct chunks.

### Friend Questions w/ Feedback

| Type | Question | Feedback |
| --- | --- | --- |
| One question I expect it should be able to do with that source available to it. | Who was Eberhart, and what happened on the expedition to Sal Vindagnyr? | Good answer. Almost all the details seem to be accurate. One small issue is that it makes it sound like it's unknown whether or not Eberhart came home when, in fact, it is known that he didn't come home. The part that is unknown is what happened instead. My best guess is that it didn't read all the way to the very last bullet point in that section of the timeline, since it's framing does match what the bullet point right before it says. |
| One question that seems plausible to do but requires some reasonable inference/analysis/knowlege beyond what is said in the source (to demonstrate it can answer questions that it should be able to answer but doesn't have a direct answer in the source, without hallucinating). | What was happening in Mondstadt around the time of the Sakoku Decree? | Disappointing answer. The timeline definitely does mention the Sakoku Decree and places it ar \[sic\] one year ago. Maybe it struggled with the exact matching of a proper noun if the RAG relies on embeddings only. Or maybe it was just that it was looking for Sakoku Decree and Monstadt together, which resulted in the actual mention of the Sakoku Decree not coming up since it wasn't brought up in the context of Monstadt. This one was also challenging because it required first knowing/finding out when the Sakoku decree was and then finding the corresponding time in Monstadt's recent history, which means it either needs to be able to do a multi-step lookup to answer this, or it would have needed to rely on having pre-existing timeline knowlege to just assume one year ago, without lookup, and focus on finding information about what was going on in Monstadt a year ago. |
| One question that shouldn't be possible to answer (to see that it doesn't hallucinate). | Who challenged the Raiden Shogun to a duel before the throne over the Vision Hunt Decree, and what was his name? | This answer was good. It was a test against hallucinating and/or over-relying on unconfirmed training data knowlege, as fans often refer to this unnamed character as Tomo, which a lot of LLMs seem to know, but it's a totally fan-made name. And this one would have been "tempting" to hallucinate or apply pre-existing knowlege since the page doesn't specifically flag it as unknown, but it did not give in to this. |

#### Additional Feedback

High level feedback across all of the answers - it's pretty good. It was able to retrieve relatively obscure information, and avoid hallucinating on questions that feel like it should have an answer. 

##### Stylistic:

Overall fine, but it does feel like it's a little too transparent about its technical mechanisms to feel like it's a "historian", eg. Saying things about the provided "context" not having the information, rather than framing it as being information it's simply doesn't know. As a development prototype, it's probably a good thing to get that transparency because it makes troubleshooting easier, but when it's closer to a finished product, it may be better for it to lean into its "persona" a little but more, to feel like a historian sharing her knowlege, or explaining that certain things are not known when an answer isn't available, rather than exposing that it's just a retrieval bot.

##### Technical:

May want to figure out why it couldn't find Sakoku decree anywhere in the text, when the name is in fact on the page. And may want to find a way to do multi step research if/when a first try doesn't find an answer.

Eg. if it failed that question because looking for "Monstadt" and "Sakoku Decree" near each other in the text brought up no results, it should have been able to look up those terms seperately (to learn the Sakoku Decree was a year ago) and then do a followup search for Monstadt a year ago. I think this would help bring it a step beyond just being just a "fuzzy text search and summarize" bot, into actually being able to answer complex lore questions
