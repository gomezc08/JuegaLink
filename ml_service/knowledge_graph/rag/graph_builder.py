"""Module for creating our graph"""

from langgraph.graph import StateGraph, END
from .nodes import Nodes
from .state import State

class GraphBuilder:
    def __init__(self):
        self.nodes = Nodes()
        self.graph = None
    
    def build_graph(self):
        """
        Build the graph
        Returns:
            StateGraph
        """
        # create state graph.
        builder = StateGraph(State)

        # Nodes.
        builder.add_node("retriever", self.nodes.retrieve_docs)
        builder.add_node("responder", self.nodes.generate_answer)
        builder.set_entry_point("retriever")

        # Edges.
        builder.add_edge("retriever", "responder")
        builder.add_edge("responder", END)

        # Graph.
        self.graph = builder.compile()
        return self.graph
    
    def run(self, query: str):
        """
        Run the graph
        Args:
            query: Query to run
        Returns:
            Response
        """
        if self.graph is None:
            self.build_graph()
        
        # initalize the state.
        inital_state = State(query = query)
        return self.graph.invoke(inital_state)
