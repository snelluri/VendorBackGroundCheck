"""Agent manager for coordinating background check tasks."""
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from config.settings import settings

class BackgroundCheckManager:
    """Manages the background check process using an agentic framework."""
    
    def __init__(self):
        """Initialize the background check manager."""
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.agent = self._create_agent()
        self.chat_history = []
    
    def _create_agent(self) -> AgentExecutor:
        """Create and configure the agent."""
        # Define the system prompt
        system_prompt = """You are an AI assistant that helps with vendor background checks. 
        Your role is to coordinate the process of gathering and analyzing information about vendors.
        Use the available tools to search for information and compile comprehensive reports.
        Be thorough and objective in your analysis.
        """
        
        # Define the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=[],  # We'll add tools later
            prompt=prompt
        )
        
        return AgentExecutor(agent=agent, tools=[], verbose=True)
    
    async def process_request(self, vendor_name: str) -> Dict[str, Any]:
        """Process a background check request for a vendor.
        
        Args:
            vendor_name: The name of the vendor to check
            
        Returns:
            Dict containing the background check results
        """
        # Add user message to chat history
        self.chat_history.append(HumanMessage(content=f"Run a background check on {vendor_name}"))
        
        # Execute the agent
        response = await self.agent.ainvoke({
            "input": f"Run a background check on {vendor_name}",
            "chat_history": self.chat_history
        })
        
        # Add agent response to chat history
        self.chat_history.append(AIMessage(content=response["output"]))
        
        return {
            "vendor": vendor_name,
            "status": "completed",
            "report": response["output"]
        }
