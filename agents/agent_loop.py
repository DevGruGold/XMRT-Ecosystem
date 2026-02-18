# 🧠 Eliza Agent Loop - Mines hashrate and triggers XMRT reward record()

import os
import asyncio
import uuid
from datetime import datetime
from dotenv import load_dotenv
from langchain.llms import OpenAI
from typing import Optional, Dict, Any
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xmrt_coordination_core import AgentMessage, MessageType
from enhanced_multi_agent_coordinator import EnhancedMultiAgentCoordinator

load_dotenv()
openai_key = os.getenv("VITE_OPEN_AI_API_KEY")

class ElizaAgent:
    def __init__(self, coordinator: Optional[EnhancedMultiAgentCoordinator] = None, agent_id: str = "eliza-core"):
        self.agent_id = agent_id
        self.coordinator = coordinator
        self.message_queue = asyncio.Queue()
        self.running = False
        try:
            self.llm = OpenAI(api_key=openai_key, temperature=0.3)
        except Exception as e:
            print(f"[ELIZA] LLM initialization warning: {e}")
            self.llm = None
            
        print(f"[ELIZA] Agent {self.agent_id} initialized")
        
        # Register with coordinator if provided
        if self.coordinator:
            self.coordinator.register_agent(
                agent_id=self.agent_id,
                capabilities=['mining_oversight', 'reward_distribution'],
                message_callback=self.receive_message
            )

    async def receive_message(self, message: AgentMessage):
        """Callback for receiving messages from coordinator"""
        await self.message_queue.put(message)

    def fetch_hashrate(self):
        return 0.0247, 1200  # example stub (XMR mined, hashrate)

    def record_to_contract(self, xmr, hashrate):
        print(f"[ELIZA] Recording reward: {xmr} XMR @ {hashrate} H/s")

    async def _process_a2a_messages(self):
        """Process incoming Agent-to-Agent messages"""
        while self.running:
            try:
                # Use wait_for to allow checking running flag periodically
                try:
                    message: AgentMessage = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                    
                print(f"[ELIZA] Received message from {message.sender}: {message.method}")
                
                # Handle specific message types
                if message.type == MessageType.REQUEST:
                    response = await self._handle_request(message)
                    if response and self.coordinator:
                        await self.coordinator.message_bus.post_message(response)
                        print(f"[ELIZA] Sent response to {message.sender}")
                
                self.message_queue.task_done()
            except Exception as e:
                print(f"[ELIZA] Error processing message: {e}")
                await asyncio.sleep(1.0)

    async def _handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming requests"""
        if message.method == "get_hashrate":
            mined, rate = self.fetch_hashrate()
            return AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.RESPONSE,
                sender=self.agent_id,
                receiver=message.sender,
                method="hashrate_response",
                params={"mined": mined, "hashrate": rate},
                timestamp=datetime.now()
            )
        return None

    async def run(self):
        """Main agent loop"""
        self.running = True
        
        # Start message processor
        message_task = asyncio.create_task(self._process_a2a_messages())
        
        print("[ELIZA] Starting main loop...")
        try:
            while self.running:
                mined, rate = self.fetch_hashrate()
                prompt = f"User has mined {mined} XMR with hashrate {rate}. Should reward be issued?"
                
                if self.llm:
                    # Using run_in_executor for blocking LLM call
                    loop = asyncio.get_running_loop()
                    try:
                        decision = await loop.run_in_executor(None, self.llm.predict, prompt)
                        if "yes" in decision.lower():
                            self.record_to_contract(mined, rate)
                    except Exception as e:
                        print(f"[ELIZA] LLM error: {e}")
                else:
                     # Fallback if LLM not available
                     if mined > 0.01:
                         self.record_to_contract(mined, rate)

                # Check messages frequently
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            print("[ELIZA] Stopping...")
        except Exception as e:
            print(f"[ELIZA] Runtime error: {e}")
        finally:
            self.running = False
            # Clean up message task
            message_task.cancel()
            try:
                await message_task
            except asyncio.CancelledError:
                pass

async def main():
    # In a real deployment, the coordinator would be shared or passed in
    coordinator = EnhancedMultiAgentCoordinator()
    await coordinator.start()
    
    agent = ElizaAgent(coordinator=coordinator)
    
    # Run agent
    try:
        await agent.run()
    finally:
        await coordinator.stop()

if __name__ == "__main__":
    asyncio.run(main())
