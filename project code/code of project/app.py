def generate_quiz(input_text: str, level: str, model, tokenizer, device):
    if len(input_text.split()) < 20:
        passage_prompt = (
            f"Write a short passage (3-4 sentences) about {input_text} for a {level} level student."
        )
        inputs = tokenizer(passage_prompt, return_tensors="pt").to(device)
        passage_output = model.generate(**inputs, max_new_tokens=100, do_sample=True, temperature=0.7)
        passage = tokenizer.decode(passage_output[0], skip_special_tokens=True)
    else:
        passage = input_text

    quiz_prompt = (
        f"You are an educational AI assistant. Read the following passage and generate 3 multiple-choice questions "
        f"based on its content, appropriate for a {level} level student.\n\n"
        f"PASSAGE:\n\"\"\"\n{passage}\n\"\"\"\n\n"
        "Each question must include:\n"
        "- A single clearly correct answer\n"
        "- Three incorrect but plausible (similar) distractor options\n"
        "- All answer options labeled A, B, C, D\n"
        "- The correct answer indicated at the end like: Answer: <option letter>\n\n"
        "Format:\n"
        "Q: <question>\n"
        "A. <option A>\n"
        "B. <option B>\n"
        "C. <option C>\n"
        "D. <option D>\n"
        "Answer: <correct option letter>\n\n"
        "Make sure the distractors are grammatically and semantically similar to the correct answer."
    )

    try:
        inputs = tokenizer(quiz_prompt, return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_new_tokens=512, do_sample=True, temperature=0.7)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        if not response or "Q:" not in response:
            raise ValueError("Invalid response from model.")

        questions = []
        for q_block in response.strip().split("Q:")[1:]:
            lines = q_block.strip().split("\n")
            if len(lines) < 6:
                continue

            question = lines[0].strip()
            options = [l[3:].strip() for l in lines[1:5]]
            answer_line = lines[5].strip()
            answer_letter = answer_line.split(":")[-1].strip().upper()
            answer_index = {"A": 0, "B": 1, "C": 2, "D": 3}.get(answer_letter, None)

            if answer_index is not None and 0 <= answer_index < len(options):
                answer = options[answer_index]
                questions.append({
                    "question": question,
                    "options": options,
                    "answer": answer
                })
        return questions

    except Exception as e:
        print(f"[Quiz Generation Error] {e}")
        return [{
            "question": "Failed to generate quiz.",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A"
        }]