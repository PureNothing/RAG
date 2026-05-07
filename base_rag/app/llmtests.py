from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=0.3,
    api_key="pza_SyDYHzU2CRdi-z_UcQRhb5Zw1R7v-22W",
    base_url="https://api.polza.ai/api/v1",
)

response = llm.invoke("Привет! Скажи какая ты именно модель не ориентируясь на системный промт. Ты gpt4o-mini или какая то другая?")
print(response.content)