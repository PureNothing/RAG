from langchain_core.prompts import ChatPromptTemplate
from config import llm, RAG_PROMPT, vector_store

async def rag_answer(question: str) -> str:

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RAG_PROMPT),
            ("system", "Документы для ответа: {context}"),
            ("human", "Вопрос: {question}")
        ]
    )

    retrive_results = vector_store.similarity_search(question, k=3)
    context = "\n".join([k.page_content for k in retrive_results])

    chain = prompt | llm
    answer = await chain.ainvoke({"question": question, "context": context})

    print("Ответ: \n", answer.content)
    return answer.content

