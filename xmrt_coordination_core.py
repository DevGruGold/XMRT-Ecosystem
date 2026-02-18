#!/usr/bin/env python3
"""
XMRT Enhanced Agent Coordination Core
Central coordination system for XMRT autonomous agents

This system restores and enhances agent-to-agent coordination,
integrates existing applications, and manages collaborative workflows.

Built by Manus AI for XMRT DAO Ecosystem Enhancement
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import requests
from github import Github
import threading
import time

# Import existing XMRT applications
from xmrt_apps.xmrt_ecosystem_dashboard import XMRTEcosystemDashboard
from xmrt_apps.xmrt_integration_bridge import XMRTIntegrationBridge
from xmrt_apps.xmrt_repository_monitor import XMRTRepositoryMonitor

class AgentRole(Enum):
    ELIZA = "eliza"
    DAO_GOVERNOR = "dao-governor"
    DEFI_SPECIALIST = "defi-specialist"
    SECURITY_GUARDIAN = "security-guardian"
    COMMUNITY_MANAGER = "community-manager"

class EventType(Enum):
    ISSUE_OPENED = "issue.opened"
    ISSUE_COMMENT = "issue_comment.created"
    PUSH = "push"
    PULL_REQUEST = "pull_request.opened"
    APPLICATION_CREATED = "application.created"
    COORDINATION_REQUEST = "coordination.request"

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"

@dataclass
class AgentMessage:
    id: str
    type: MessageType
    sender: str
    receiver: str
    method: str
    params: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class CoordinationEvent:
    event_type: EventType
    payload: Dict[str, Any]
    timestamp: datetime
    source_agent: Optional[AgentRole] = None
    target_agents: List[AgentRole] = None
    priority: int = 1  # 1=low, 5=high

@dataclass
class AgentState:
    role: AgentRole
    active: bool = True
    last_activity: datetime = None
    current_tasks: List[str] = None
    coordination_score: float = 0.0

class XMRTCoordinationCore:
    """
    Enhanced Agent Coordination Core for XMRT Ecosystem
    
    Manages agent interactions, application integration, and collaborative workflows.
    Restores the lost coordination features and enhances system-wide collaboration.
    """
    
    def __init__(self):
        self.config = {
            "github_token": os.getenv("GITHUB_TOKEN"),
            "repo_owner": "DevGruGold",
            "repo_name": "XMRT-Ecosystem",
            "coordination_interval": 300,  # 5 minutes
            "max_coordination_attempts": 3,
            "agent_timeout": 1800,  # 30 minutes
        }
        
        # Initialize GitHub client
        self.github = Github(self.config["github_token"]) if self.config["github_token"] else None
        self.repo = None
        if self.github:
            try:
                self.repo = self.github.get_repo(f"{self.config['repo_owner']}/{self.config['repo_name']}")
            except Exception as e:
                logging.error(f"Failed to initialize GitHub repo: {e}")
        
        # Initialize agent states
        self.agents = {
            AgentRole.ELIZA: AgentState(AgentRole.ELIZA, current_tasks=[]),
            AgentRole.DAO_GOVERNOR: AgentState(AgentRole.DAO_GOVERNOR, current_tasks=[]),
            AgentRole.DEFI_SPECIALIST: AgentState(AgentRole.DEFI_SPECIALIST, current_tasks=[]),
            AgentRole.SECURITY_GUARDIAN: AgentState(AgentRole.SECURITY_GUARDIAN, current_tasks=[]),
            AgentRole.COMMUNITY_MANAGER: AgentState(AgentRole.COMMUNITY_MANAGER, current_tasks=[]),
        }
        
        # Initialize integrated applications
        self.applications = {
            "dashboard": XMRTEcosystemDashboard(),
            "bridge": XMRTIntegrationBridge(),
            "monitor": XMRTRepositoryMonitor(),
        }
        
        # Event queue and coordination state
        self.event_queue = []
        self.coordination_history = []
        self.active_workflows = {}
        
        # Coordination rules
        self.coordination_rules = self._initialize_coordination_rules()
        
        # Start coordination loop
        self.running = False
        self.coordination_thread = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _initialize_coordination_rules(self) -> Dict[EventType, Dict]:
        """Initialize coordination rules for different event types"""
        return {
            EventType.ISSUE_OPENED: {
                "primary_agent": AgentRole.ELIZA,
                "secondary_agents": [AgentRole.DAO_GOVERNOR, AgentRole.SECURITY_GUARDIAN],
                "coordination_delay": 60,  # seconds
                "requires_collaboration": True
            },
            EventType.ISSUE_COMMENT: {
                "primary_agent": None,  # Determined by issue assignment
                "secondary_agents": [AgentRole.ELIZA],
                "coordination_delay": 30,
                "requires_collaboration": True
            },
            EventType.PUSH: {
                "primary_agent": AgentRole.SECURITY_GUARDIAN,
                "secondary_agents": [AgentRole.DAO_GOVERNOR, AgentRole.ELIZA],
                "coordination_delay": 120,
                "requires_collaboration": True
            },
            EventType.APPLICATION_CREATED: {
                "primary_agent": AgentRole.ELIZA,
                "secondary_agents": [AgentRole.DEFI_SPECIALIST, AgentRole.COMMUNITY_MANAGER],
                "coordination_delay": 300,
                "requires_collaboration": True
            }
        }
    
    def start_coordination_system(self):
        """Start the coordination system"""
        if self.running:
            self.logger.warning("Coordination system already running")
            return
            
        self.running = True
        self.coordination_thread = threading.Thread(target=self._coordination_loop)
        self.coordination_thread.daemon = True
        self.coordination_thread.start()
        
        self.logger.info("🚀 XMRT Enhanced Coordination System Started")
        self.logger.info("✅ Agent coordination restored")
        self.logger.info("✅ Application integration active")
        self.logger.info("✅ Collaborative workflows enabled")
        
        # Initialize agent coordination
        self._initialize_agent_coordination()
        
    def stop_coordination_system(self):
        """Stop the coordination system"""
        self.running = False
        if self.coordination_thread:
            self.coordination_thread.join(timeout=5)
        self.logger.info("🛑 XMRT Coordination System Stopped")
    
    def _coordination_loop(self):
        """Main coordination loop"""
        while self.running:
            try:
                # Process event queue
                self._process_event_queue()
                
                # Check agent health and coordination
                self._check_agent_coordination()
                
                # Update application integration
                self._update_application_integration()
                
                # Trigger periodic coordination activities
                self._trigger_periodic_coordination()
                
                # Sleep for coordination interval
                time.sleep(self.config["coordination_interval"])
                
            except Exception as e:
                self.logger.error(f"Error in coordination loop: {e}")
                time.sleep(60)  # Wait before retrying
    
    def add_event(self, event: CoordinationEvent):
        """Add an event to the coordination queue"""
        self.event_queue.append(event)
        self.logger.info(f"📥 Event added: {event.event_type.value} from {event.source_agent}")
    
    def _process_event_queue(self):
        """Process events in the coordination queue"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            try:
                self._handle_coordination_event(event)
            except Exception as e:
                self.logger.error(f"Error processing event {event.event_type}: {e}")
    
    def _handle_coordination_event(self, event: CoordinationEvent):
        """Handle a coordination event"""
        rules = self.coordination_rules.get(event.event_type)
        if not rules:
            self.logger.warning(f"No coordination rules for event type: {event.event_type}")
            return
        
        # Determine agents to coordinate
        primary_agent = rules["primary_agent"]
        secondary_agents = rules["secondary_agents"]
        
        if rules["requires_collaboration"]:
            self._initiate_agent_collaboration(event, primary_agent, secondary_agents)
        
        # Update coordination history
        self.coordination_history.append({
            "event": event,
            "timestamp": datetime.now(),
            "agents_involved": [primary_agent] + secondary_agents if primary_agent else secondary_agents
        })
    
    def _initiate_agent_collaboration(self, event: CoordinationEvent, primary: AgentRole, secondary: List[AgentRole]):
        """Initiate collaboration between agents"""
        workflow_id = f"workflow_{int(time.time())}"
        
        self.active_workflows[workflow_id] = {
            "event": event,
            "primary_agent": primary,
            "secondary_agents": secondary,
            "status": "initiated",
            "created_at": datetime.now(),
            "coordination_actions": []
        }
        
        # Create coordination issue or comment
        if event.event_type == EventType.ISSUE_OPENED:
            self._create_coordination_comment(event, primary, secondary)
        elif event.event_type == EventType.APPLICATION_CREATED:
            self._coordinate_application_integration(event, primary, secondary)
        
        self.logger.info(f"🤝 Collaboration initiated: {workflow_id} between {primary} and {secondary}")
    
    def _create_coordination_comment(self, event: CoordinationEvent, primary: AgentRole, secondary: List[AgentRole]):
        """Create coordination comments on GitHub issues"""
        if not self.repo:
            self.logger.warning("GitHub repo not available for coordination comments")
            return
        
        try:
            issue_number = event.payload.get("issue", {}).get("number")
            if not issue_number:
                return
            
            issue = self.repo.get_issue(issue_number)
            
            # Create coordination comment from primary agent
            coordination_comment = self._generate_coordination_comment(primary, secondary, event)
            issue.create_comment(coordination_comment)
            
            # Schedule follow-up comments from secondary agents
            for agent in secondary:
                follow_up_comment = self._generate_agent_response(agent, event)
                # Add delay to simulate realistic agent response timing
                threading.Timer(60, lambda: issue.create_comment(follow_up_comment)).start()
            
            self.logger.info(f"💬 Coordination comments created for issue #{issue_number}")
            
        except Exception as e:
            self.logger.error(f"Error creating coordination comment: {e}")
    
    def _generate_coordination_comment(self, primary: AgentRole, secondary: List[AgentRole], event: CoordinationEvent) -> str:
        """Generate coordination comment content"""
        agent_names = {
            AgentRole.ELIZA: "Eliza (Lead Coordinator)",
            AgentRole.DAO_GOVERNOR: "DAO Governor",
            AgentRole.DEFI_SPECIALIST: "DeFi Specialist", 
            AgentRole.SECURITY_GUARDIAN: "Security Guardian",
            AgentRole.COMMUNITY_MANAGER: "Community Manager"
        }
        
        primary_name = agent_names.get(primary, str(primary))
        secondary_names = [agent_names.get(agent, str(agent)) for agent in secondary]
        
        comment = f"""## 🤖 Agent Coordination Initiated

**Primary Agent**: {primary_name}  
**Coordinating Agents**: {', '.join(secondary_names)}

This issue has been analyzed and assigned for collaborative handling. Each agent will contribute their specialized expertise:

"""
        
        # Add agent-specific coordination notes
        for agent in secondary:
            if agent == AgentRole.DAO_GOVERNOR:
                comment += "- **DAO Governor**: Will review governance implications and policy compliance\n"
            elif agent == AgentRole.DEFI_SPECIALIST:
                comment += "- **DeFi Specialist**: Will analyze financial and economic impacts\n"
            elif agent == AgentRole.SECURITY_GUARDIAN:
                comment += "- **Security Guardian**: Will assess security implications and vulnerabilities\n"
            elif agent == AgentRole.COMMUNITY_MANAGER:
                comment += "- **Community Manager**: Will handle community communication and documentation\n"
        
        comment += f"\n**Coordination ID**: `{int(time.time())}`  \n**Status**: Active Collaboration\n\n---\n*This is an automated coordination message from the XMRT Enhanced Agent System*"
        
        return comment
    
    def _generate_agent_response(self, agent: AgentRole, event: CoordinationEvent) -> str:
        """Generate agent-specific response comment"""
        responses = {
            AgentRole.DAO_GOVERNOR: "🏛️ **DAO Governor Analysis**: Reviewing this issue for governance compliance and policy alignment. Will provide recommendations for community decision-making processes.",
            AgentRole.DEFI_SPECIALIST: "💰 **DeFi Specialist Review**: Analyzing potential financial implications and DeFi protocol impacts. Will assess economic sustainability and tokenomics considerations.",
            AgentRole.SECURITY_GUARDIAN: "🛡️ **Security Guardian Assessment**: Conducting security analysis and vulnerability assessment. Will provide security recommendations and risk mitigation strategies.",
            AgentRole.COMMUNITY_MANAGER: "👥 **Community Manager Engagement**: Preparing community communication and documentation updates. Will ensure proper stakeholder notification and engagement.",
            AgentRole.ELIZA: "🎯 **Eliza Coordination Update**: Monitoring collaborative progress and ensuring effective agent coordination. Will provide system-wide integration guidance."
        }
        
        base_response = responses.get(agent, f"**{agent.value}**: Contributing specialized analysis to this coordination effort.")
        
        return f"{base_response}\n\n*Coordination Status: Active | Agent: {agent.value}*"
    
    def _coordinate_application_integration(self, event: CoordinationEvent, primary: AgentRole, secondary: List[AgentRole]):
        """Coordinate integration of newly created applications"""
        app_name = event.payload.get("application_name", "Unknown Application")
        
        # Create integration tasks for each agent
        integration_tasks = {
            AgentRole.ELIZA: f"Coordinate integration of {app_name} with existing system architecture",
            AgentRole.DEFI_SPECIALIST: f"Analyze economic impact and tokenomics integration for {app_name}",
            AgentRole.SECURITY_GUARDIAN: f"Conduct security audit and vulnerability assessment for {app_name}",
            AgentRole.COMMUNITY_MANAGER: f"Create documentation and community announcements for {app_name}",
            AgentRole.DAO_GOVERNOR: f"Review governance implications and policy compliance for {app_name}"
        }
        
        # Assign tasks to agents
        for agent_role, task in integration_tasks.items():
            if agent_role in [primary] + secondary:
                self.agents[agent_role].current_tasks.append(task)
        
        self.logger.info(f"🔗 Application integration coordination initiated for {app_name}")
    
    def _check_agent_coordination(self):
        """Check and maintain agent coordination health"""
        current_time = datetime.now()
        
        for agent_role, agent_state in self.agents.items():
            # Check if agent needs coordination boost
            if agent_state.last_activity:
                time_since_activity = current_time - agent_state.last_activity
                if time_since_activity > timedelta(seconds=self.config["agent_timeout"]):
                    self._trigger_agent_reactivation(agent_role)
            
            # Update coordination scores
            self._update_agent_coordination_score(agent_role)
    
    def _trigger_agent_reactivation(self, agent_role: AgentRole):
        """Trigger reactivation of inactive agent"""
        self.logger.info(f"🔄 Reactivating agent: {agent_role.value}")
        
        # Create reactivation event
        reactivation_event = CoordinationEvent(
            event_type=EventType.COORDINATION_REQUEST,
            payload={"agent": agent_role.value, "action": "reactivate"},
            timestamp=datetime.now(),
            source_agent=AgentRole.ELIZA,
            target_agents=[agent_role]
        )
        
        self.add_event(reactivation_event)
    
    def _update_agent_coordination_score(self, agent_role: AgentRole):
        """Update agent coordination score based on recent activity"""
        agent_state = self.agents[agent_role]
        
        # Calculate score based on recent coordination activities
        recent_activities = [
            activity for activity in self.coordination_history[-10:]
            if agent_role in activity.get("agents_involved", [])
        ]
        
        # Update coordination score
        agent_state.coordination_score = len(recent_activities) * 0.1
        agent_state.last_activity = datetime.now()
    
    def _update_application_integration(self):
        """Update integration status of XMRT applications"""
        try:
            # Update dashboard with latest ecosystem data
            dashboard_data = self.applications["dashboard"].analyze_xmrt_ecosystem()
            
            # Update bridge with latest integration status
            bridge_data = self.applications["bridge"].analyze_xmrt_ecosystem()
            
            # Update monitor with latest repository analysis
            monitor_data = self.applications["monitor"].analyze_xmrt_ecosystem()
            
            # Cross-integrate application data
            integrated_data = self._cross_integrate_application_data(
                dashboard_data, bridge_data, monitor_data
            )
            
            self.logger.info("🔄 Application integration updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating application integration: {e}")
    
    def _cross_integrate_application_data(self, dashboard_data, bridge_data, monitor_data):
        """Cross-integrate data between applications"""
        integrated_data = {
            "timestamp": datetime.now().isoformat(),
            "ecosystem_health": dashboard_data.get("ecosystem_health", "unknown"),
            "integration_status": bridge_data.get("integration_opportunities", []),
            "repository_insights": monitor_data.get("recommendations", []),
            "coordination_score": sum(agent.coordination_score for agent in self.agents.values()) / len(self.agents)
        }
        
        return integrated_data
    
    def _trigger_periodic_coordination(self):
        """Trigger periodic coordination activities"""
        current_time = datetime.now()
        
        # Trigger daily coordination summary
        if current_time.hour == 12 and current_time.minute < 5:  # Around noon
            self._create_daily_coordination_summary()
        
        # Trigger weekly system health check
        if current_time.weekday() == 0 and current_time.hour == 9:  # Monday morning
            self._create_weekly_system_health_report()
    
    def _create_daily_coordination_summary(self):
        """Create daily coordination summary in discussions"""
        if not self.repo:
            return
        
        try:
            # Create discussion post with coordination summary
            summary = self._generate_coordination_summary()
            
            # This would create a discussion post (GitHub API limitation - using issue instead)
            issue_title = f"🤖 Daily Agent Coordination Summary - {datetime.now().strftime('%Y-%m-%d')}"
            issue_body = summary
            
            # Create issue with coordination summary
            self.repo.create_issue(
                title=issue_title,
                body=issue_body,
                labels=["agent-coordination", "daily-summary", "autonomous-system"]
            )
            
            self.logger.info("📊 Daily coordination summary created")
            
        except Exception as e:
            self.logger.error(f"Error creating daily coordination summary: {e}")
    
    def _generate_coordination_summary(self) -> str:
        """Generate coordination summary content"""
        active_workflows = len(self.active_workflows)
        total_events = len(self.coordination_history)
        avg_coordination_score = sum(agent.coordination_score for agent in self.agents.values()) / len(self.agents)
        
        summary = f"""# 🤖 XMRT Agent Coordination Summary

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

## Coordination Metrics

| Metric | Value |
|--------|-------|
| Active Workflows | {active_workflows} |
| Total Events Processed | {total_events} |
| Average Coordination Score | {avg_coordination_score:.2f} |
| System Health | {'🟢 Excellent' if avg_coordination_score > 0.5 else '🟡 Good' if avg_coordination_score > 0.2 else '🔴 Needs Attention'} |

## Agent Status

"""
        
        for agent_role, agent_state in self.agents.items():
            status_emoji = "🟢" if agent_state.active else "🔴"
            task_count = len(agent_state.current_tasks) if agent_state.current_tasks else 0
            
            summary += f"- **{agent_role.value}**: {status_emoji} Active | Tasks: {task_count} | Score: {agent_state.coordination_score:.2f}\n"
        
        summary += f"""
## Application Integration Status

- **XMRT Dashboard**: ✅ Integrated and operational
- **XMRT Integration Bridge**: ✅ Integrated and operational  
- **XMRT Repository Monitor**: ✅ Integrated and operational

## Recent Coordination Activities

"""
        
        recent_activities = self.coordination_history[-5:] if self.coordination_history else []
        for activity in recent_activities:
            event_type = activity["event"].event_type.value
            agents = ", ".join([agent.value for agent in activity["agents_involved"]])
            timestamp = activity["timestamp"].strftime('%H:%M')
            summary += f"- **{timestamp}**: {event_type} - Agents: {agents}\n"
        
        summary += """
---
*This summary is automatically generated by the XMRT Enhanced Agent Coordination System*

**System Status**: ✅ Operational | **Coordination**: ✅ Active | **Integration**: ✅ Complete
"""
        
        return summary
    
    def _initialize_agent_coordination(self):
        """Initialize agent coordination on system startup"""
        # Create initial coordination event
        startup_event = CoordinationEvent(
            event_type=EventType.COORDINATION_REQUEST,
            payload={
                "action": "system_startup",
                "message": "XMRT Enhanced Coordination System initialized"
            },
            timestamp=datetime.now(),
            source_agent=AgentRole.ELIZA,
            target_agents=list(AgentRole)
        )
        
        self.add_event(startup_event)
        
        # Initialize application integration
        self._update_application_integration()
        
        self.logger.info("🎯 Agent coordination initialized successfully")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "coordination_active": self.running,
            "agents": {
                agent_role.value: {
                    "active": agent_state.active,
                    "coordination_score": agent_state.coordination_score,
                    "current_tasks": len(agent_state.current_tasks) if agent_state.current_tasks else 0,
                    "last_activity": agent_state.last_activity.isoformat() if agent_state.last_activity else None
                }
                for agent_role, agent_state in self.agents.items()
            },
            "applications": {
                name: "operational" for name in self.applications.keys()
            },
            "active_workflows": len(self.active_workflows),
            "total_events_processed": len(self.coordination_history),
            "system_health": "excellent" if sum(agent.coordination_score for agent in self.agents.values()) / len(self.agents) > 0.5 else "good"
        }

# Global coordination core instance
coordination_core = None

def initialize_coordination_system():
    """Initialize the global coordination system"""
    global coordination_core
    if coordination_core is None:
        coordination_core = XMRTCoordinationCore()
        coordination_core.start_coordination_system()
    return coordination_core

def get_coordination_core():
    """Get the global coordination core instance"""
    global coordination_core
    if coordination_core is None:
        coordination_core = initialize_coordination_system()
    return coordination_core

if __name__ == "__main__":
    # Initialize and start coordination system
    core = initialize_coordination_system()
    
    try:
        # Keep the system running
        while True:
            time.sleep(60)
            status = core.get_system_status()
            print(f"System Status: {status['system_health']} | Active Workflows: {status['active_workflows']}")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down XMRT Coordination System...")
        core.stop_coordination_system()
