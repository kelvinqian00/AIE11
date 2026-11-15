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

**What I changed**

I decided to add a functionality to save the embeddings to a local file.

**Why**

I noticed that I was burning nearly 60k tokens with each prompt just on running the embedding model on the source documents, so doing so saved some token costs. (After all, real RAG systems persist the embeddings in vector DBs.)

**What would change my mind**

If this were a more complicated system where saving the embeddings somehow caused bugs or other issues (or if tokens were literally free).
