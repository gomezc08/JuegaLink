"""LangGraph nodes for RAG workflow + ReAct Agent inside generate_content"""

import logging
from typing import List, Optional
from .state import State

logger = logging.getLogger(__name__)

from langchain_core.documents import Document
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage
from .rag_chain import RAGChain

try:
    from langgraph.prebuilt import create_react_agent
    _HAS_REACT_AGENT = True
except Exception:
    _HAS_REACT_AGENT = False

try:
    from langchain_community.utilities import WikipediaAPIWrapper
    _HAS_WIKI = True
except Exception:
    _HAS_WIKI = False


class _StubRetriever:
    def invoke(self, query: str) -> List[Document]:
        return []


class Nodes:
    def __init__(self, retriever, llm, username: str = None, history: list = None):
        self.retriever = retriever if retriever is not None else _StubRetriever()
        self.llm = llm
        self.username = username or ""
        self.history = history if history is not None else []
        self.rag_chain = RAGChain(username=self.username, history=self.history)
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
        return State(question=state.question, retrieved_docs=docs)

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
        
        # 2. Graph Cypher QA Chain – user/graph lookups
        def graph_cypher_qa_chain_tool_fn(question: str) -> str:
            return self.rag_chain.query_rag_chain(question, update_history=False)

        # 3. Wikipedia
        def wikipedia_tool_fn(question: str) -> str:
            if not _HAS_WIKI:
                return "Wikipedia not available."
            try:
                wrapper = WikipediaAPIWrapper(top_k_results=3, lang="en")
                return wrapper.run(question)
            except Exception as e:
                return f"Wikipedia error: {e}"

        return [
            Tool(
                name="juegalink_retriever",
                func=retriever_tool_fn,
                description="Retrieve JuegaLink documentation: app basics, how to use features, account, events, fields. Use for questions about what JuegaLink is or how it works.",
            ),
            Tool(
                name="graph_cypher_qa",
                func=graph_cypher_qa_chain_tool_fn,
                description="Query the current user's graph: friends count, my events, who I follow, my posts. Use for questions about the logged-in user (e.g. 'how many friends do I have?', 'what events am I in?').",
            ),
            Tool(
                name="wikipedia",
                func=wikipedia_tool_fn,
                description="Search Wikipedia for general knowledge. Use for factual or encyclopedic questions not about JuegaLink or the user.",
            ),
        ]
    
    def build_agent(self):
        tools = self.build_tools()
        if _HAS_REACT_AGENT:
            self.agent = create_react_agent(self.llm, tools)
        else:
            self.agent = None

    def generate_answer(self, state: State) -> State:
        if self.agent is None:
            self.build_agent()

        if self.agent is not None:
            # Include conversation history so the agent has context
            messages = []
            for q, a in self.history:
                messages.append(HumanMessage(content=q))
                messages.append(AIMessage(content=a))
            messages.append(HumanMessage(content=state.question))
            result = self.agent.invoke({"messages": messages})
            messages = result.get("messages", [])
            # Log which tools were used
            tools_used = []
            for msg in messages:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                        if name:
                            tools_used.append(name)
            if tools_used:
                logger.info("RAG agent tools used: %s", tools_used)
            answer = None
            if messages:
                last = messages[-1]
                answer = getattr(last, "content", None)
            answer = answer or "Could not generate answer."
        else:
            answer = self.rag_chain.query_rag_chain(state.question)

        return State(
            question=state.question,
            retrieved_docs=state.retrieved_docs,
            answer=answer,
        )