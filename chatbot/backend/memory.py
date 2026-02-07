from collections import deque

# store last 5 interactions
chat_memory = deque(maxlen=5)

def add_to_memory(question: str, answer: str):
    chat_memory.append({
        "question": question,
        "answer": answer
    })

def get_memory_context():
    if not chat_memory:
        return ""

    history = ""
    for idx, item in enumerate(chat_memory, 1):
        history += f"""
Previous Q{idx}: {item['question']}
Previous A{idx}: {item['answer']}
"""
    return history
