from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from fastapi.responses import StreamingResponse
from qdrant_client.models import Prefetch, FusionQuery, Fusion, NamedVector, NamedSparseVector, SparseVector
from app.rag.config import llm, RAG_PROMPT, qdrant_client, reranker_bge_v2_m3, embedding_model_bge_m3, bm25_model_qdrantmb25, settings
from app.rag.rag_data import user_collection_name
from app.rag.funcs import get_session_history, clear_session_history
from app.logger import logger

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_PROMPT),
        ("system", "Документы для ответа: {context}"),
        ("placeholder", "{history}"),
        ("human", "Вопрос пользователя: {question}")
    ]
)

chain = prompt | llm

chat = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history"
)

async def hybrid_search(question: str, user_id: int, top_k: int = 20) -> list[dict]:
    collection_name = user_collection_name(user_id=user_id)

    exists = await qdrant_client.collection_exists(collection_name=collection_name)
    if not exists:
        logger.info("Пользователь запросил ответ но в его истории нет никаких документов.")
        return []
    
    dense_vector = embedding_model_bge_m3.embed_query(question)
    sparse_vector = list(bm25_model_qdrantmb25.embed([question]))[0]

    results = await qdrant_client.query_points(
        collection_name=collection_name,
        prefetch=[
            Prefetch(
                query=dense_vector,
                using="dense",
                limit=top_k,
            ),
            Prefetch(
                query=SparseVector(
                        indices=sparse_vector.indices.tolist(),
                        values=sparse_vector.values.tolist(),
                    ),
                    using="sparse",
                    limit=top_k
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "text": point.payload["text"],
            "source": point.payload.get("source", ""),
            "title": point.payload.get("title", ""),
            "score": point.score,
        }
        for point in results.points
    ]

async def rerank(question: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    
    pairs = [(question, candidate["text"]) for candidate in candidates]
    scores = reranker_bge_v2_m3.score(pairs)

    for candidate, score in zip(candidates, scores):
        candidate["reranker_score"] = float(score)

    reranked = sorted(candidates, key=lambda candidate_arg: candidate_arg["reranker_score"], reverse=True)

    return reranked[:top_k]

async def rag_answer(question: str, session_id: str, user_id: int) -> StreamingResponse:
    logger.debug("Получен запрос на ответ запускаю пайплайн.")
    try:
        candidates = await hybrid_search(question=question, user_id=user_id)
        logger.info(f"Получено кандидатов: {len(candidates)}")

        if not candidates:
            async def no_data_stream():
                yield "data: У вас нет загруженных документов, загрузите их через /upload_url\n\n"
                yield "data [DONE]\n\n"
            return StreamingResponse(no_data_stream(), media_type="text/event-stream")
        
        top_docs = await rerank(question=question, candidates=candidates, top_k=5)
        logger.debug(f"После Rerank топ 1 score = {top_docs[0]["reranker_score"]:3f}")

        context = "\n\n---\n\n".join(f"Источник: {doc["source"]}\n\n {doc["text"]}" for doc in top_docs)

        async def stream_tokens():
            async for chunk in chat.astream(
                {"question": question,
                "context": context},
                config={"configurable": {"session_id": session_id}}
            ):
                if chunk.content:
                    yield f"data: {chunk.content}\n\n"
                
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            stream_tokens(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )
    
    except Exception as e:
        logger.error(f"Ошибка при попытке получить ответ. {e}")
        raise