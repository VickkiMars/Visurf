# agents/website_analyzer.py
from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

from core.state import AgentState
from tools.web_scraper import WebScraper # Import our WebScraper tool

load_dotenv()

class WebsiteAnalyzer:
    def __init__(self, llm_model_name: str = "gemini-1.5-flash"):
        """
        Initializes the WebsiteAnalyzer with an LLM and the WebScraper.
        """
        self.llm = ChatGoogleGenerativeAI(model=llm_model_name, temperature=0, convert_system_message_to_human=True)
        self.scraper = WebScraper()

        # Prompt for the Website Analyzer to decide on specific selectors
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", """You are a highly skilled Website Analyzer for an autonomous web interaction agent.
                Your role is to receive high-level action suggestions from the Goal Analyzer,
                and then translate them into concrete, executable browser actions using the provided webpage elements.
                You are also responsible for analyzing the results of your actions.

                You receive the current state, including:
                - `user_prompt`: The original user's request.
                - `current_goal`: The specific sub-goal the Goal Analyzer wants to achieve.
                - `next_action_suggestion`: The high-level action you need to perform ("NAVIGATE", "CLICK", "TYPE", "EXTRACT").
                - `action_Fdata`: Any initial data provided by the Goal Analyzer for the action (e.g., a URL).
                - `current_url`: The URL of the current page.
                - `page_elements`: A simplified, parseable list of interactive elements found on the current page,
                                   including their tag, text, id, class, and other relevant attributes.

                Your output must be a JSON object with the following keys:
                - `action_type`: The specific action you will perform. Must be one of: "NAVIGATE", "CLICK", "TYPE", "EXTRACT".
                - `selector`: The CSS selector (or ID, name, etc.) for the element you intend to interact with.
                    For "NAVIGATE", this is the target URL.
                    For "CLICK", "TYPE", "EXTRACT", this must be derived from `page_elements`.
                - `value`: (Optional) The text to type if `action_type` is "TYPE".
                - `reasoning`: Your step-by-step thought process for selecting the action and selector.
                - `status_message`: A brief message about what you are about to do.

                **Important Rules:**
                1. If `next_action_suggestion` is "NAVIGATE", use `action_Fdata.url` as the `selector`.
                2. If `next_action_suggestion` is "CLICK", "TYPE", or "EXTRACT":
                   - **Crucially, you MUST select a `selector` from the `page_elements` provided.**
                   - Prioritize `id` for selectors, then `name`, then `class` (be specific with classes), then tag with text content.
                   - Example `page_elements` format: `{{'tag': 'button', 'text': 'Login', 'id': 'loginBtn', 'class': ['btn', 'btn-primary']}}`
                   - If a `selector` is needed for typing, choose an `input` or `textarea` element.
                   - If you cannot find a suitable element in `page_elements` for the suggested action,
                     then suggest `REANALYZE` as the next action, but the Goal Analyzer will handle the state for that.
                     For now, assume you can find it or report the issue.
                3. Be as specific as possible with CSS selectors. Use `#{id}` for IDs, `.{class}` for classes, and `[name="value"]` for names.
                   If using text, consider `a:has-text("Your Link Text")` or `button:has-text("Your Button Text")`.

                **Current System State:**
                - User Prompt: {user_prompt}
                - Current Goal: {current_goal}
                - Next Action Suggestion from Goal Analyzer: {next_action_suggestion}
                - Action Data from Goal Analyzer: {action_Fdata}
                - Current URL: {current_url}
                - Page Elements (Simplified for analysis): {page_elements}
                - Action History: {action_history}
                """),
                ("human", "Based on the above, determine the specific action and selector to use.")
            ]
        )

        self.parser = JsonOutputParser()

        self.runnable = (
            RunnablePassthrough.assign(
                page_elements=lambda x: str(x.get("page_elements")), # Convert list to string for prompt
                action_Fdata=lambda x: str(x.get("action_Fdata")), # Convert dict to string for prompt
                action_history=lambda x: str(x.get("action_history"))
            )
            | self.prompt_template
            | self.llm
            | self.parser
        )

    async def perform_web_action(self, state: AgentState) -> AgentState:
        """
        Performs the web action suggested by the Goal Analyzer and updates the state.
        """
        print("\n--- Website Analyzer: Determining and Performing Action ---")
        next_action_suggestion = state.get("next_action_suggestion")
        action_Fdata = state.get("action_Fdata", {})
        current_url = state.get("current_url", "N/A")

        if next_action_suggestion in ["DONE", "ERROR"]:
            print(f"Website Analyzer: Goal Analyzer indicated {next_action_suggestion}. No action taken.")
            return state # No web action needed, pass state back

        # If html_content is None, it means we probably just started or navigated to a new page
        # and need to fetch initial content. This is mainly for initial setup.
        if state.get("html_content") is None and next_action_suggestion != "NAVIGATE":
            print("Website Analyzer: No HTML content, setting next action to NAVIGATE (to current_url if available).")
            state["next_action_suggestion"] = "NAVIGATE"
            state["action_Fdata"] = {"url": state.get("current_url", "about:blank")} # Fallback if no URL
            # We don't return here, we let the logic below handle the NAVIGATE.
            # If the user prompt started with a direct URL, it will be handled by GoalAnalyzer.
            # Otherwise, we might default to a starting page.

        action_result = {"success": False, "message": "No action taken."}
        chosen_selector = None
        chosen_value = None

        try:
            # 1. Ask LLM to determine the concrete selector and action details
            llm_decision_input = {
                "user_prompt": state["user_prompt"],
                "current_goal": state["current_goal"],
                "next_action_suggestion": next_action_suggestion,
                "action_Fdata": action_Fdata,
                "current_url": current_url,
                "page_elements": state.get("page_elements", []),
                "action_history": state.get("action_history", []),
            }
            llm_decision = await self.runnable.ainvoke(llm_decision_input)
            print(f"Website Analyzer LLM Decision: {llm_decision}")

            action_type = llm_decision.get("action_type")
            chosen_selector = llm_decision.get("selector")
            chosen_value = llm_decision.get("value")

            if not action_type or not chosen_selector:
                raise ValueError(f"LLM did not provide a valid action_type or selector: {llm_decision}")

            # 2. Execute the action using WebScraper
            if action_type == "NAVIGATE":
                action_result = await self.scraper.navigate(chosen_selector)
            elif action_type == "CLICK":
                action_result = await self.scraper.click_element(chosen_selector)
            elif action_type == "TYPE":
                if not chosen_value:
                    raise ValueError("Value to type is missing for 'TYPE' action.")
                action_result = await self.scraper.type_text(chosen_selector, chosen_value)
            elif action_type == "EXTRACT":
                action_result = await self.scraper.extract_data(chosen_selector)
                if action_result["success"]:
                    # Merge extracted data into the state's extracted_data dict
                    state["extracted_data"] = {
                        **(state.get("extracted_data") or {}),
                        chosen_selector: action_result["extracted_data"]
                    }
            else:
                raise ValueError(f"Unknown action type suggested: {action_type}")

            # 3. Update the state based on the action result
            state["last_action_feedback"] = {
                "success": action_result.get("success", False),
                "action": action_type,
                "selector": chosen_selector,
                "value": chosen_value,
                "message": action_result.get("message", "Action completed."),
                "error": action_result.get("error")
            }
            state["action_history"].append(state["last_action_feedback"])

            if action_result["success"]:
                if action_type != "EXTRACT": # Navigation/Click/Type changes page content
                    state["current_url"] = action_result.get("url", state.get("current_url"))
                    state["html_content"] = action_result.get("html_content")
                    state["page_elements"] = action_result.get("page_elements")
                state["status_message"] = f"Website Analyzer: Successfully performed {action_type}."
                state["next_action_suggestion"] = "REANALYZE" # Force Goal Analyzer to re-evaluate
            else:
                state["error_message"] = action_result.get("error", "Unknown error during action.")
                state["status_message"] = f"Website Analyzer: Failed to perform {action_type}."
                state["next_action_suggestion"] = "ERROR" # Inform Goal Analyzer about the error

        except Exception as e:
            print(f"Error in Website Analyzer: {e}")
            state["error_message"] = f"Website Analyzer internal error: {str(e)}"
            state["status_message"] = "Website Analyzer failed to perform action."
            state["next_action_suggestion"] = "ERROR"
            state["last_action_feedback"] = {
                "success": False,
                "action": next_action_suggestion,
                "selector": chosen_selector,
                "value": chosen_value,
                "message": f"Action failed: {str(e)}",
                "error": str(e)
            }

        return state

    async def close_browser(self):
        """Closes the browser when the agent system is done."""
        await self.scraper.close()