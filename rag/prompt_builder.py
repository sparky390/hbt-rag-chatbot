def build_prompt(query: str, context: list):
    prompt = "You are an assistant answering questions using HBT knowledge."
    prompt += "\n\nContext:\n" + "\n\n".join(context)
    prompt += f"\n\nQuestion: {query}"
    return prompt
