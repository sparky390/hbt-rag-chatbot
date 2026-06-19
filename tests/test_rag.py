from rag.prompt_builder import build_prompt


def test_build_prompt_includes_question_and_context():
    prompt = build_prompt("What is HBT?", ["HBT is a services company."])
    assert "Question: What is HBT?" in prompt
    assert "HBT is a services company." in prompt
