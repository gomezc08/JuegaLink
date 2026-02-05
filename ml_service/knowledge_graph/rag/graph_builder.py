"""Module for creating our graph"""

from langgraph.graph import StateGraph, END
from .nodes import Nodes
from .state import State


class GraphBuilder:
    def __init__(self, llm, retriever=None, username: str = None, history: list = None):
        self.llm = llm
        self.retriever = retriever
        self.username = username or ""
        self.history = history if history is not None else []
        self.nodes = Nodes(
            retriever=retriever,
            llm=llm,
            username=self.username,
            history=self.history,
        )
        self.graph = None

    def build_graph(self):
        """Build the LangGraph: single agent node with 3 tools (graph cypher QA, Wikipedia, JuegaLink retriever)."""
        builder = StateGraph(State)
        builder.add_node("responder", self.nodes.generate_answer)
        builder.set_entry_point("responder")
        builder.add_edge("responder", END)
        self.graph = builder.compile()
        return self.graph

    def run(self, query: str):
        """Run the graph and return final state (with state.answer)."""
        if self.graph is None:
            self.build_graph()
        initial_state = State(question=query)
        return self.graph.invoke(initial_state)
