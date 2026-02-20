import mlflow
from databricks.vector_search.client import VectorSearchClient
from langchain_community.vectorstores import DatabricksVectorSearch
from langchain_community.chat_models import ChatDatabricks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. Setup Clients & Configuration
catalog = "main"
schema = "default"
index_name = f"{catalog}.{schema}.my_docs_index"
endpoint_name = "databricks-llama-3-70b-instruct" # The LLM endpoint

# Initialize Vector Search
vsc = VectorSearchClient()
index = vsc.get_index(endpoint_name="one-vector-search-endpoint", index_name=index_name)

# 2. Define the Retriever
vectorstore = DatabricksVectorSearch(
    index, 
    text_column="content_text", 
    columns=["id", "content_text", "source_url"]
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 3. Define the LLM & Prompt
llm = ChatDatabricks(endpoint=endpoint_name, extra_params={"temperature": 0.1})

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# 4. Build the LangChain (LCEL)
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 5. Log the Model to Unity Catalog for Deployment
mlflow.set_registry_uri("databricks-uc")
model_name = f"{catalog}.{schema}.rag_chain_api"

with mlflow.start_run():
    # This logs the chain and its dependencies
    model_info = mlflow.langchain.log_model(
        lc_model=chain,
        artifact_path="chain",
        registered_model_name=model_name,
        pip_requirements=[
            "langchain",
            "databricks-vectorsearch",
            "mlflow",
            "pydantic==2.5.2"
        ]
    )