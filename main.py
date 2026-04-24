import json

from dotenv import load_dotenv
from openai import OpenAI

from tools import get_weather, list_notes, save_note

load_dotenv()

client = OpenAI()

TOOLS = {
    "get_weather": get_weather,
    "save_note": save_note,
    "list_notes": list_notes,
}

tool_schemas = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather in city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "save_note",
        "description": "Save note to storage",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_notes",
        "description": "Get all notes",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
]

conversation = [
    {
        "role": "system",
        "content": (
            "You are a helpful console assistant. "
            "Use tools when needed. "
            "Do not invent tool results."
        ),
    }
]

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in {"exit", "quit"}:
        break

    conversation.append({
        "role": "user",
        "content": user_input,
    })

    while True:
        response = client.responses.create(
            model="gpt-5.4",
            input=conversation,
            tools=tool_schemas,
        )

        tool_called = False
        assistant_text = []

        for item in response.output:
            if item.type == "message":
                conversation.append(item)

                for c in item.content:
                    if c.type == "output_text":
                        assistant_text.append(c.text)

            elif item.type == "function_call":
                tool_called = True

                fn_name = item.name
                args = json.loads(item.arguments)

                if fn_name not in TOOLS:
                    result = {"error": f"Unknown tool: {fn_name}"}
                else:
                    result = TOOLS[fn_name](**args)

                conversation.append(item)
                conversation.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                })

        if tool_called:
            continue

        final = "\n".join(assistant_text).strip()
        print("Bot:", final)
        break