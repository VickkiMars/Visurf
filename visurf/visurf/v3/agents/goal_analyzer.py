# agents/goal_analyzer.py
from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI # Example LLM, replace with your choice
import os
from dotenv import load_dotenv

from core.state import AgentState

load_dotenv() # Load environment variables from .env file

class GoalAnalyzer:
    def __init__(self, llm_model_name: str = "gemini-1.5-flash"):
        """
        Initializes the GoalAnalyzer with an LLM.
        """
        # Initialize your chosen LLM
        # Ensure OPENAI_API_KEY is set in your .env file or environment
        self.llm = ChatGoogleGenerativeAI(model=llm_model_name, temperature=0)

        # Define the prompt for the Goal Analyzer
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", """You are a sophisticated Goal Analyzer for an autonomous web interaction agent.
                Your primary role is to interpret a user's prompt, break it down into actionable steps,
                determine the current progress towards the goal, and suggest the next high-level action for a Website Analyzer.
                You receive the current state of the system, including the user's initial prompt,
                the current webpage content (simplified), and any actions taken so far.

                Your output must be a JSON object with the following keys:
                - `current_goal`: A concise description of the specific sub-goal currently being pursued.
                - `is_goal_achieved`: A boolean indicating if the overall user prompt goal has been fully achieved.
                - `next_action_suggestion`: The high-level action for the Website Analyzer.
                    Must be one of: "NAVIGATE", "CLICK", "TYPE", "EXTRACT", "DONE", "ERROR", "REANALYZE".
                - `action_data`: A dictionary containing specific data for the `next_action_suggestion`.
                    - If "NAVIGATE": `{{ "url": "https://example.com" }}` (only for initial navigation or direct URL)
                    - If "CLICK": `{{ "element_id": "some_id" }}` (or 'text', 'xpath' etc., depending on what Website Analyzer expects)
                    - If "TYPE": `{{ "element_id": "some_id", "text": "value_to_type" }}`
                    - If "EXTRACT": `{{ "query": "CSS selector or description of data to extract" }}`
                    - If "DONE", "ERROR", "REANALYZE": `{{}}` or `{{ "message": "reason" }}`
                - `status_message`: A brief message summarizing the current status or next step.
                - `error_message`: (Optional) A detailed error message if `next_action_suggestion` is "ERROR".

                Consider the following when making your decision:
                - **User Prompt:** "{user_prompt}"
                - **Current System State:**
                    - Current Goal: {current_goal}
                    - Sub-Goals Achieved: {sub_goals_achieved}
                    - Current URL: {current_url}
                    - Page Elements (Simplified): {page_elements}
                    - Action History: {action_history}
                    - Extracted Data: {extracted_data}
                    - Last Action Feedback: {last_action_feedback}
                - **Instructions:**
                    - If the `is_goal_achieved` is True, set `next_action_suggestion` to "DONE".
                    - If an error occurred (check `last_action_feedback` or `error_message` in state),
                      try to suggest a recovery action, or set `next_action_suggestion` to "ERROR".
                    - Use `REANALYZE` if the page content drastically changed or you need the Website Analyzer to re-evaluate without a specific action from you.
                    - Prioritize breaking down complex tasks into simple, verifiable steps.
                    - If the task is to navigate to a specific URL, set `next_action_suggestion` to "NAVIGATE" with the target URL.
                """),
                ("human", "Analyze the state and suggest the next action based on the user prompt: {user_prompt}")
            ]
        )

        self.parser = JsonOutputParser()

        # Create the Langchain runnable for the Goal Analyzer
        self.runnable = (
            RunnablePassthrough.assign(
                page_elements=lambda x: str(x.get("page_elements")), # Convert list to string for prompt
                action_history=lambda x: str(x.get("action_history")),
                sub_goals_achieved=lambda x: str(x.get("sub_goals_achieved")),
                extracted_data=lambda x: str(x.get("extracted_data")),
                last_action_feedback=lambda x: str(x.get("last_action_feedback"))
            )
            | self.prompt_template
            | self.llm
            | self.parser
        )

    async def analyze_goal(self, state: AgentState) -> AgentState:
        """
        Analyzes the current goal and state, suggesting the next action.
        """
        print("\n--- Goal Analyzer: Analyzing State ---")
        print(f"User Prompt: {state.get('user_prompt')}")
        print(f"Current URL: {state.get('current_url')}")
        # print(f"Page Elements: {state.get('page_elements')}") # Can be verbose

        # Prepare input for the runnable
        input_data = {
            "user_prompt": state["user_prompt"],
            "current_goal": state.get("current_goal", "No current goal set."),
            "sub_goals_achieved": state.get("sub_goals_achieved", []),
            "current_url": state.get("current_url", "N/A"),
            "html_content": state.get("html_content", "N/A"), # Not directly used in prompt but part of state
            "page_elements": state.get("page_elements", []),
            "action_history": state.get("action_history", []),
            "extracted_data": state.get("extracted_data", {}),
            "last_action_feedback": state.get("last_action_feedback", {}),
            "is_goal_achieved": state.get("is_goal_achieved", False),
            "status_message": state.get("status_message", "")
        }

        try:
            # Invoke the LLM to get the next action suggestion
            llm_response = await self.runnable.ainvoke(input_data)
            print(f"Goal Analyzer Output: {llm_response}")

            # Update the state based on the LLM's response
            state["current_goal"] = llm_response.get("current_goal", state.get("current_goal"))
            state["is_goal_achieved"] = llm_response.get("is_goal_achieved", False)
            state["next_action_suggestion"] = llm_response.get("next_action_suggestion", "REANALYZE")
            state["action_Fdata"] = llm_response.get("action_Fdata", {})
            state["status_message"] = llm_response.get("status_message", "Goal analysis complete.")
            state["error_message"] = llm_response.get("error_message")

        except Exception as e:
            print(f"Error in Goal Analyzer: {e}")
            state["next_action_suggestion"] = "ERROR"
            state["error_message"] = f"Goal Analyzer internal error: {str(e)}"
            state["status_message"] = "Goal analysis failed due to an internal error."

        return state