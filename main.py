#!/usr/bin/env python3
"""
XMRT DAO AI Automation Service
Autonomous AI agents for DAO operations
"""

import asyncio
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import schedule
from web3 import Web3
from eth_account import Account
import openai
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.governance_agent import GovernanceAgent
from agents.treasury_agent import TreasuryAgent
from agents.community_agent import CommunityAgent
from utils.blockchain_utils import BlockchainUtils
from utils.ai_utils import AIUtils

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIAutomationService:
    """Main AI automation service orchestrator"""

    def __init__(self):
        self.blockchain_utils = BlockchainUtils()
        self.ai_utils = AIUtils()

        # Initialize AI agents
        self.governance_agent = GovernanceAgent(self.blockchain_utils, self.ai_utils)
        self.treasury_agent = TreasuryAgent(self.blockchain_utils, self.ai_utils)
        self.community_agent = CommunityAgent(self.blockchain_utils, self.ai_utils)

        self.agents = {
            'governance': self.governance_agent,
            'treasury': self.treasury_agent,
            'community': self.community_agent
        }

        self.running = False
        self.automation_enabled = True

        logger.info("AI Automation Service initialized")

    async def start_automation(self):
        """Start the automation service"""
        logger.info("🚀 Starting AI Automation Service...")
        self.running = True

        # Schedule automated tasks
        self.schedule_tasks()

        # Start main automation loop
        while self.running:
            try:
                await self.automation_cycle()
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in automation cycle: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    def schedule_tasks(self):
        """Schedule periodic automated tasks"""
        # Governance tasks
        schedule.every(5).minutes.do(self.governance_agent.check_proposals)
        schedule.every(1).hours.do(self.governance_agent.analyze_sentiment)

        # Treasury tasks
        schedule.every(15).minutes.do(self.treasury_agent.monitor_treasury)
        schedule.every(1).hours.do(self.treasury_agent.optimize_allocations)
        schedule.every(6).hours.do(self.treasury_agent.rebalance_portfolio)

        # Community tasks
        schedule.every(1).minutes.do(self.community_agent.monitor_community)
        schedule.every(30).minutes.do(self.community_agent.generate_reports)

        logger.info("Automated tasks scheduled")

    async def automation_cycle(self):
        """Main automation cycle"""
        if not self.automation_enabled:
            return

        # Run scheduled tasks
        schedule.run_pending()

        # Check for urgent actions
        await self.check_urgent_actions()

        # Update agent status
        await self.update_agent_status()

    async def check_urgent_actions(self):
        """Check for urgent actions that need immediate attention"""
        try:
            # Check for emergency proposals
            emergency_proposals = await self.governance_agent.check_emergency_proposals()
            if emergency_proposals:
                logger.warning(f"Emergency proposals detected: {len(emergency_proposals)}")
                for proposal in emergency_proposals:
                    await self.governance_agent.handle_emergency_proposal(proposal)

            # Check treasury health
            treasury_health = await self.treasury_agent.check_treasury_health()
            if treasury_health['status'] == 'critical':
                logger.warning("Treasury health critical - taking emergency action")
                await self.treasury_agent.emergency_rebalance()

            # Check community alerts
            community_alerts = await self.community_agent.check_alerts()
            if community_alerts:
                logger.info(f"Community alerts: {len(community_alerts)}")
                for alert in community_alerts:
                    await self.community_agent.handle_alert(alert)

        except Exception as e:
            logger.error(f"Error checking urgent actions: {e}")

    async def update_agent_status(self):
        """Update status of all agents"""
        for name, agent in self.agents.items():
            try:
                status = await agent.get_status()
                logger.debug(f"{name} agent status: {status}")
            except Exception as e:
                logger.error(f"Error updating {name} agent status: {e}")

    def stop_automation(self):
        """Stop the automation service"""
        logger.info("🛑 Stopping AI Automation Service...")
        self.running = False

    def enable_automation(self):
        """Enable automation"""
        self.automation_enabled = True
        logger.info("✅ Automation enabled")

    def disable_automation(self):
        """Disable automation"""
        self.automation_enabled = False
        logger.info("⏸️ Automation disabled")

    async def execute_manual_action(self, agent_name: str, action: str, params: Dict[str, Any]):
        """Execute a manual action through an agent"""
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")

        agent = self.agents[agent_name]
        result = await agent.execute_action(action, params)

        logger.info(f"Manual action executed - Agent: {agent_name}, Action: {action}, Result: {result}")
        return result

    def get_system_status(self):
        """Get overall system status"""
        return {
            'running': self.running,
            'automation_enabled': self.automation_enabled,
            'agents': {name: agent.is_active() for name, agent in self.agents.items()},
            'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0,
            'last_cycle': datetime.now().isoformat()
        }

async def main():
    """Main entry point"""
    service = AIAutomationService()
    service.start_time = time.time()

    try:
        await service.start_automation()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        service.stop_automation()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
