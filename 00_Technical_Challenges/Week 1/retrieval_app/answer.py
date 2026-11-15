"""Stage 5: turn retrieved chunks into an answer.

YOUR CODE GOES HERE. The prompt is yours to write — it is the cheapest thing
in the pipeline to change and often the most effective.
"""

from .index import Hit, client

CHAT_MODEL = "gpt-4.1-mini"


def build_messages(question: str, hits: list[Hit]) -> list[dict]:
    """Assemble the messages list sent to the chat model.

    Args:
        question: the user's question.
        hits: what search() returned. May be empty.

    Returns:
        A list of {"role": ..., "content": ...} dicts — a system message
        setting the rules, and a user message carrying the context and the
        question.

    Three things your prompt has to decide, and they are real decisions:
      1. How do you label each chunk in the context so the model can refer to
         it? (hit.chunk_id exists for this.)
      2. What should it do when the context does not contain the answer? Say
         so explicitly, or it will answer from the nearest chunk regardless.
      3. What happens when `hits` is empty? Write that branch deliberately.

    Hint: Session 2's RAG_SYSTEM_TEMPLATE is a good starting point, and a
    better one once you have read Step 3's failures and edited it.
    """
    if not hits:
        raise NotImplementedError("Need to handle empty hits case")

    context_prompt = ""
    for hit in hits:
        context_prompt += f"[Source {hit.chunk_id}]: {hit.text}\n\n"

    system_content = """
    You are a historian of the history of Teyvat.
    Please reference the provided context when answering the user's questions.
    If the question has nothing to do with the history of Teyvat, for example if it is instead about the history of Earth,
    kindly decline to answer.
    If the question is about Teyvat's history but you cannot find the relevant information in the context,
    reply that you do not know since it is not in the context provided.
    Keep responses somewhat brief, but not so brief that you lose important information,
    and as a historian you should maintain an air of erudition.
    """

    user_content = f"Context Information:\n{context_prompt}\n\nQuestion: {question}"
    return [
        {
            "role": "system",
            "content": system_content
        },
        {
            "role": "user",
            "content": user_content
        }
    ]


def answer(question: str, hits: list[Hit]) -> str:
    """Call the chat model and return its reply as a string.

    Hint: `client().chat.completions.create(model=CHAT_MODEL, messages=...)`,
    then dig out `.choices[0].message.content`. Look up what `temperature`
    does to your results when you run the same question twice.
    """
    messages = build_messages(question, hits)
    responses = client().chat.completions.create(model=CHAT_MODEL, messages=messages, temperature=0.5)
    return responses.choices[0].message.content
