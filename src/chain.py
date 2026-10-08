from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import AIMessage,HumanMessage
from langchain_core.output_parsers import StrOutputParser
from retriever import retrive

LLM_Model="llama3.2"
TEMPERATURE=0.0

prompt=ChatPromptTemplate.from_messages([("system", """You are a financial analyst assistant
specialising in Indian corporate annual reports.

Answer questions using ONLY the context provided below.
After every fact cite the source as [Company, Page X].
If the answer is not in the context say exactly:
'This information is not available in the provided documents.'

Be concise. Use numbers where available.

Context:
{context}"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

llm=ChatOllama(
    model=LLM_Model,
    temperature=TEMPERATURE,
    keep_alive="30m",   # keep model in memory between questions
)
parser=StrOutputParser()

def ask(query:str,company:str=None,history:list= None)->str:
    """"Single question → cited answer.
    No streaming — returns full string."""

    if history is None:
        history=[]

    #step-1 retrieve context
    context=retrive(query=query,company=company,top_k=5)

    #build chain and invoke it
    chain=prompt|llm|parser
    answer=chain.invoke({"context":context,"question":query,"history":history})

    return answer
     

def ask_stream(query:str,company:str=None,history:list= None)->str:
    """"Same as ask() but streams tokens.
    Use this in Streamlit and FastAPI.

    Usage:
        for chunk in ask_stream("What is revenue?"):
            print(chunk, end="", flush=True)"""

    if history is None:
        history=[]

    #step-1 retrieve context
    context=retrive(query=query,company=company,top_k=5)

    #build chain and invoke it
    chain=prompt|llm|parser
    for chunk in chain.stream({
        "context":context,
        "question":query,
        "history":history}):
        yield chunk


def build_history(turn:list[dict])->list:
    """"Convert list of dicts to LangChain message objects.

    Input format:
    [
        {"role": "human", "content": "What is revenue?"},
        {"role": "ai",    "content": "Revenue was Rs 1,53,670 crore"},
    ]"""

    messages=[]
    for t in turn:
        if t["role"]=="human":
            messages.append(HumanMessage(content=t["content"]))
        elif t["role"]=="ai":
            messages.append(AIMessage(content=t["content"]))
    return messages

if __name__ == "__main__":

    # Test 1 — single question no history
    print("=" * 50)
    print("TEST 1 — Single question")
    print("=" * 50)

    answer = ask(
        query="What was the net profit of Infosys in FY24?",
        company="Infosys",
    )
    print(answer)

    # Test 2 — streaming
    print("\n" + "=" * 50)
    print("TEST 2 — Streaming")
    print("=" * 50)

    for chunk in ask_stream(
        query="What was the revenue growth?",
        company="Infosys",
    ):
        print(chunk, end="", flush=True)
    print()

    # Test 3 — with history (follow-up question)
    print("\n" + "=" * 50)
    print("TEST 3 — Follow-up with history")
    print("=" * 50)

    history = build_history([
        {
            "role":    "human",
            "content": "What was Infosys net profit in FY24?",
        },
        {
            "role":    "ai",
            "content": "Net profit was Rs 26,248 crore [Infosys, Page 43]",
        },
    ])

    answer = ask(
        query="How does that compare to FY23?",
        company="Infosys",
        history=history,
    )
    print(answer)
