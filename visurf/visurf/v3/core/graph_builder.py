# core/graph_builder.py
from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.goal_analyzer import GoalAnalyzer
from agents.website_analyzer import WebsiteAnalyzer
import asyncio

def create_graph():
    """
    Creates and compiles the langgraph graph that orchestrates the GoalAnalyzer and WebsiteAnalyzer.
    """
    # Instantiate your agents
    goal_analyzer_agent = GoalAnalyzer()
    website_analyzer_agent = WebsiteAnalyzer()

    # Define the graph
    graph = StateGraph(AgentState)

    # Add nodes for each agent.
    # The string key (e.g., "goal_analyzer") is the node's name in the graph.
    graph.add_node("goal_analyzer", goal_analyzer_agent.analyze_goal)
    graph.add_node("website_analyzer", website_analyzer_agent.perform_web_action)

    # Set the entry point of the graph.
    # The first step will always be handled by the Goal Analyzer.
    graph.set_entry_point("goal_analyzer")

    # Define the conditional edge from the Goal Analyzer.
    # The 'should_continue' function determines the next node based on the state.
    def should_continue(state: AgentState):
        """
        Determines the next step after the Goal Analyzer has run.
        If the goal is achieved or an error occurred, the graph ends.
        Otherwise, it continues to the Website Analyzer.
        """
        if state["next_action_suggestion"] in ["DONE", "ERROR"]:
            return "end"
        else:
            return "continue_to_website_analyzer" # This string maps to a node or END

    graph.add_conditional_edges(
        "goal_analyzer",      # Source node
        should_continue,      # Function to call to decide next step
        {
            "continue_to_website_analyzer": "website_analyzer", # If "continue", go to website_analyzer node
            "end": END                                        # If "end", terminate the graph
        }
    )

    # Define the edge from the Website Analyzer.
    # After the Website Analyzer performs an action, it always goes back to the Goal Analyzer
    # for re-evaluation of the new state.
    graph.add_edge("website_analyzer", "goal_analyzer")

    # Compile the graph
    # This locks the graph structure and prepares it for execution.
    compiled_graph = graph.compile()

    # Store references to agents in the compiled graph for cleanup
    # This is a common pattern to ensure resources (like browser instances) are closed.
    compiled_graph.goal_analyzer_agent = goal_analyzer_agent
    compiled_graph.website_analyzer_agent = website_analyzer_agent

    return compiled_graph