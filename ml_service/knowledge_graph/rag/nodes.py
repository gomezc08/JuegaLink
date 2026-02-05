"""LangGraph nodes for RAG workflow + ReAct Agent inside generate_content"""

from typing import List, Optional
from .state import State

from langchain_core.documents import Document
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

# Wikipedia tool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun

class Nodes:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        self.agent = None
    
    def retrieve_docs(self, state: State) -> State:
        """
        Retrieve documents from the retriever
        Args:
            state: State
        Returns:
            State
        """
        docs = self.retriever.invoke(state.question)
        return State (
            question = state.question,
            retrieved_docs = docs
        )

    def build_tools(self) -> List[Tool]:
        """
        Build tools for the ReAct Agent
        Returns:
            List of tools
        """
        # 1. retriever tool.
        def retriever_tool_fn(question: str) -> str:
            docs: List[Document] = self.retriever.invoke(question)
            if not docs:
                return "No documents found."
            merged = []
            for i, d in enumerate(docs[:8], start=1):
                meta = d.metadata if hasattr(d, "metadata") else {}
                title = meta.get("title") or meta.get("source") or f"doc_{i}"
                merged.append(f"[{i}] {title}\n{d.page_content}")
            return "\n\n".join(merged)
        
        # 2. wikipedia tool.
        def wikipedia_tool_fn(question: str) -> str:
            wikipedia = WikipediaAPIWrapper(
                api_wrapper = WikipediaAPIWrapper(top_k_results=3, lang = "en")
            )
            return wikipedia.run(question)
        
        # create tools.
        retriever_tool = Tool(
            name = "retriever",
            func = retriever_tool_fn,
            description = "Retrieve documents from the retriever"
        )

        wikipedia_tool = Tool(
            name = "wikipedia",
            func = wikipedia_tool_fn,
            description = "Search Wikipedia for information"
        )

        return [retriever_tool, wikipedia_tool]
    
    def build_agent(self):
        """
        Build the ReAct Agent
        Returns:
            ReAct Agent
        """
        tools = self.build_tools()
        system_prompt = """
            "You are a helpful RAG agent."
            "Prefer 'retriever' for user-provided docs; use 'wikipedia' for general knowledge."
            "Return only the final useful answer, do not include any other text."
        """
        self.agent = create_agent(
            llm = self.llm,
            tools = tools,
            prompt = system_prompt
        )
    
    def generate_answer(self, state: State) -> State:
        """
        Generate answer using the ReAct Agent
        Args:
            state: State
        Returns:
            State
        """
        if self.agent is None:
            self.build_agent()
        
        # invoke the agent.
        result = self.agent.invoke({"messages": [HumanMessage(content = state.question)]})

        messages = result.get("messages", [])
        answer: Optional[str] = None
        if messages:
            answer_msg = messages[-1]
            answer = getattr(answer_msg, "content", None)
        
        return State(
            question=state.question,
            retrieved_docs=state.retrieved_docs,
            answer=answer or "Could not generate answer."
        )