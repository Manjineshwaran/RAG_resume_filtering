import json
import google.generativeai as genai
from tools.resume_retriever_tool import ResumeRetrieverTool
from google.adk.agents import Agent
from agents.prompt import *

# --- Mock Agent Framework --- #

class LlmAgent:
    def __init__(self, name, model, instruction, tools=None, output_key=None):
        self.name = name
        self.model = model
        self.instruction = instruction
        self.tools = tools or []
        self.output_key = output_key

    def run(self, input_data):
        print(f"--- Running {self.name} ---")
        if self.tools:
            tool = self.tools[0]
            tool_input = input_data.get('parsed_query', {})
            print(f"Using tool with input: {tool_input}")
            return tool.run(tool_input)
        else:
            prompt = self.instruction.format(**input_data)
            response = self.model.generate_content(prompt)
            return response.text

class SequentialAgent:
    def __init__(self, name, sub_agents, description):
        self.name = name
        self.sub_agents = sub_agents
        self.description = description

    def run(self, input_data):
        context = {"initial_input": input_data}
        for agent in self.sub_agents:
            # Format instruction with available context
            formatted_instruction = agent.instruction.format(**context)
            current_agent_input = {**context, '_instruction': formatted_instruction}
            
            # Run the agent
            output = agent.run(current_agent_input)

            # Print the raw output for debugging
            print(f"\n--- Output from {agent.name} ---")
            print(output)
            print("-" * (20 + len(agent.name)) + "\n")
            
            # Clean and store output
            if agent.output_key:
                if isinstance(output, str):
                    cleaned_output = output.strip().replace("```json", "").replace("```", "")
                    try:
                        context[agent.output_key] = json.loads(cleaned_output)
                    except json.JSONDecodeError:
                        context[agent.output_key] = cleaned_output # Store as text if not valid JSON
                else:
                    context[agent.output_key] = output # Directly store non-string output
            context[f'{agent.name}_output'] = output # also store raw output
        return context

# --- Agent Definitions --- #
genai.configure(api_key="API KEY") 
GEMINI_MODEL = genai.GenerativeModel('gemini-2.0-flash')

query_parser_agent = LlmAgent(
    name="QueryParserAgent",
    model=GEMINI_MODEL,
    instruction=query_parser_agent_prompt,
    output_key="parsed_query"
)

resume_retriever_agent = LlmAgent(
    name="ResumeRetrieverAgent",
    model=GEMINI_MODEL, # Not used, tool is called directly
    tools=[ResumeRetrieverTool()],
    instruction=resume_retriever_agent_prompt,
    output_key="retrieved_resumes"
)

resume_ranker_agent = LlmAgent(
    name="ResumeRankerAgent",
    model=GEMINI_MODEL,
    instruction='''
Given a list of resumes and a parsed query, rank the top 5 candidates based on how well they match the skills and experience.

Here is the user's query: {parsed_query}

Here are the resumes: {retrieved_resumes}

Output a JSON list where each item has "name", "score" (from 0 to 100), and a short "reason" for the ranking.
''',
    output_key="ranked_resumes"
)

formatter_agent = LlmAgent(
    name="FormatterAgent",
    model=GEMINI_MODEL,
    instruction='''
Format the following ranked list of resumes into a clean, easy-to-read bulleted list. For each candidate, display their name, score, and the reason for their ranking.

Ranked Resumes: {ranked_resumes}

Return plain text only.
''',
    output_key="final_output"
)

resume_pipeline_agent = SequentialAgent(
    name="ResumePipelineAgent",
    sub_agents=[
        resume_retriever_agent,
        resume_ranker_agent,
        formatter_agent
    ],
    description="Pipeline for parsing query, retrieving and ranking resumes."
)

root_agent = resume_pipeline_agent

# Wrap SequentialAgent inside ADK Agent
# root_agent = Agent(
#     name="resume_pipeline_agent",
#     description="Pipeline for parsing query, retrieving and ranking resumes.",
#     run=resume_pipeline_agent.run
# )
