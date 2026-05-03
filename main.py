import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from tools import get_weather, list_notes, save_note

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4o"),
    temperature=0,
)
memory = MemorySaver()

tools = [
    get_weather,
    save_note,
    list_notes,
]

system_prompt = """
Ты консольный ассистент.

Ты умеешь:
- отвечать на обычные вопросы пользователя;
- получать погоду через инструмент get_weather;
- сохранять заметки через инструмент save_note;
- показывать заметки через инструмент list_notes.

Правила:
- если пользователь просит сохранить заметку, используй save_note;
- если пользователь спрашивает про сохранённые заметки, используй list_notes;
- если пользователь спрашивает погоду, используй get_weather;
- не выдумывай результаты инструментов;
- отвечай кратко и по делу;
- отвечай на русском языке.
"""

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory,
)


def chat(user_input: str) -> str:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config={
            "configurable": {"thread_id": "default_cli_session"},
            "recursion_limit": 20,
        },
    )

    final = next(
        m for m in reversed(result["messages"])
        if isinstance(m, AIMessage) and m.content
    )

    return final.content


def main() -> None:
    print("CLI LangChain Agent. Напиши 'exit' для выхода.")

    while True:
        user_input = input("\nТы: ").strip()

        if user_input.lower() in {"exit", "quit", "выход"}:
            print("Пока!")
            break

        answer = chat(user_input)
        print(f"\nБот: {answer}")


if __name__ == "__main__":
    main()