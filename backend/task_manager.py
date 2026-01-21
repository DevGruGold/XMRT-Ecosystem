#!/usr/bin/env python3
'''
XMRT Ecosystem Automated Task Management and Agent Coordination System
Handles autonomous task assignment, execution, and coordination between AI agents
'''

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import uuid

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentSpecialization(Enum):
    GOVERNANCE = "governance"
    DEFI = "defi"
    SECURITY = "security"
    COMMUNITY = "community"
    DEVELOPMENT = "development"

@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: TaskPriority
    specialization: AgentSpecialization
    created_at: datetime
    deadline: Optional[datetime] = None
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    result: Optional[Dict[str, Any]] = None
    dependencies: List[str] = None
    estimated_duration: Optional[int] = None  # in minutes
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class Agent:
    id: str
    name: str
    specialization: AgentSpecialization
    capabilities: List[str]
    current_tasks: List[str]
    max_concurrent_tasks: int = 3
    performance_score: float = 1.0
    availability: bool = True
    last_active: datetime = None
    
    def __post_init__(self):
        if self.current_tasks is None:
            self.current_tasks = []
        if self.last_active is None:
            self.last_active = datetime.now()

class TaskManager:
    '''Automated task management and agent coordination system'''
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.task_queue: Dict[TaskPriority, List[str]] = {
            priority: [] for priority in TaskPriority
        }
        self.running = False
        self.coordination_rules = []
        self.performance_metrics = {}
        
        # Initialize default agents
        self._initialize_agents()
        self._load_coordination_rules()
    
    def _initialize_agents(self):
        '''Initialize AI agents with their capabilities'''
        default_agents = [
            Agent(
                id="xmrt_dao_governor",
                name="XMRT DAO Governor",
                specialization=AgentSpecialization.GOVERNANCE,
                capabilities=[
                    "proposal_analysis", "voting_coordination", "treasury_management",
                    "governance_monitoring", "community_coordination", "decision_making"
                ],
                current_tasks=[]
            ),
            Agent(
                id="xmrt_defi_specialist",
                name="XMRT DeFi Specialist",
                specialization=AgentSpecialization.DEFI,
                capabilities=[
                    "yield_optimization", "liquidity_management", "risk_analysis",
                    "market_monitoring", "protocol_integration", "financial_planning"
                ],
                current_tasks=[]
            ),
            Agent(
                id="xmrt_security_guardian",
                name="XMRT Security Guardian",
                specialization=AgentSpecialization.SECURITY,
                capabilities=[
                    "threat_detection", "vulnerability_scanning", "incident_response",
                    "security_monitoring", "risk_assessment", "emergency_protocols"
                ],
                current_tasks=[]
            ),
            Agent(
                id="xmrt_community_manager",
                name="XMRT Community Manager",
                specialization=AgentSpecialization.COMMUNITY,
                capabilities=[
                    "engagement_tracking", "event_coordination", "sentiment_analysis",
                    "social_monitoring", "content_creation", "relationship_building"
                ],
                current_tasks=[]
            )
        ]
        
        for agent in default_agents:
            self.agents[agent.id] = agent
            logger.info(f"Initialized agent: {agent.name}")
    
    def _load_coordination_rules(self):
        '''Load agent coordination rules'''
        self.coordination_rules = [
            {
                "rule": "security_veto",
                "description": "Security Guardian has veto power on all financial operations",
                "condition": lambda task: task.specialization == AgentSpecialization.DEFI,
                "required_agents": ["xmrt_security_guardian"]
            },
            {
                "rule": "governance_oversight",
                "description": "DAO Governor oversees all major decisions",
                "condition": lambda task: task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH],
                "required_agents": ["xmrt_dao_governor"]
            },
            {
                "rule": "community_notification",
                "description": "Community Manager notified of public-facing changes",
                "condition": lambda task: "public" in task.description.lower(),
                "required_agents": ["xmrt_community_manager"]
            }
        ]
    
    def create_task(self, title: str, description: str, priority: TaskPriority, 
                   specialization: AgentSpecialization, deadline: Optional[datetime] = None,
                   dependencies: List[str] = None, estimated_duration: Optional[int] = None) -> str:
        '''Create a new task'''
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            specialization=specialization,
            created_at=datetime.now(),
            deadline=deadline,
            dependencies=dependencies or [],
            estimated_duration=estimated_duration
        )
        
        self.tasks[task_id] = task
        self.task_queue[priority].append(task_id)
        
        logger.info(f"Created task: {title} (ID: {task_id})")
        
        # Trigger immediate assignment for critical tasks
        if priority == TaskPriority.CRITICAL:
            self._assign_task(task_id)
        
        return task_id
    
    def _assign_task(self, task_id: str) -> bool:
        '''Assign task to the most suitable agent'''
        task = self.tasks.get(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False
        
        # Check dependencies
        if not self._check_dependencies(task):
            logger.info(f"Task {task_id} waiting for dependencies")
            return False
        
        # Find suitable agents
        suitable_agents = self._find_suitable_agents(task)
        
        if not suitable_agents:
            logger.warning(f"No suitable agents found for task {task_id}")
            return False
        
        # Select best agent based on performance and availability
        selected_agent = self._select_best_agent(suitable_agents, task)
        
        if selected_agent:
            # Assign task
            task.assigned_agent = selected_agent.id
            task.status = TaskStatus.ASSIGNED
            selected_agent.current_tasks.append(task_id)
            selected_agent.last_active = datetime.now()
            
            # Remove from queue
            self.task_queue[task.priority].remove(task_id)
            
            logger.info(f"Assigned task {task_id} to agent {selected_agent.name}")
            
            # Apply coordination rules
            self._apply_coordination_rules(task)
            
            return True
        
        return False
    
    def _check_dependencies(self, task: Task) -> bool:
        '''Check if all task dependencies are completed'''
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _find_suitable_agents(self, task: Task) -> List[Agent]:
        '''Find agents suitable for the task'''
        suitable_agents = []
        
        for agent in self.agents.values():
            if (agent.specialization == task.specialization and
                agent.availability and
                len(agent.current_tasks) < agent.max_concurrent_tasks):
                suitable_agents.append(agent)
        
        return suitable_agents
    
    def _select_best_agent(self, agents: List[Agent], task: Task) -> Optional[Agent]:
        '''Select the best agent for the task based on performance and workload'''
        if not agents:
            return None
        
        # Score agents based on performance, workload, and specialization match
        scored_agents = []
        
        for agent in agents:
            score = agent.performance_score
            
            # Prefer agents with lower current workload
            workload_factor = 1.0 - (len(agent.current_tasks) / agent.max_concurrent_tasks)
            score *= workload_factor
            
            # Bonus for exact capability match
            required_capabilities = self._extract_required_capabilities(task)
            capability_match = len(set(required_capabilities) & set(agent.capabilities))
            if capability_match > 0:
                score *= (1.0 + capability_match * 0.1)
            
            scored_agents.append((score, agent))
        
        # Return agent with highest score
        scored_agents.sort(key=lambda x: x[0], reverse=True)
        return scored_agents[0][1]
    
    def _extract_required_capabilities(self, task: Task) -> List[str]:
        '''Extract required capabilities from task description'''
        # Simple keyword matching - could be enhanced with NLP
        capability_keywords = {
            "analysis": ["analysis", "analyze", "review"],
            "monitoring": ["monitor", "watch", "track"],
            "optimization": ["optimize", "improve", "enhance"],
            "coordination": ["coordinate", "manage", "organize"],
            "security": ["secure", "protect", "audit"],
            "communication": ["communicate", "notify", "announce"]
        }
        
        required_capabilities = []
        description_lower = task.description.lower()
        
        for capability, keywords in capability_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                required_capabilities.append(capability)
        
        return required_capabilities
    
    def _apply_coordination_rules(self, task: Task):
        '''Apply coordination rules for multi-agent tasks'''
        for rule in self.coordination_rules:
            if rule["condition"](task):
                for agent_id in rule["required_agents"]:
                    if agent_id != task.assigned_agent:
                        # Create coordination task
                        coord_task_id = self.create_task(
                            title=f"Coordination: {task.title}",
                            description=f"Coordinate on task: {task.description}",
                            priority=task.priority,
                            specialization=self.agents[agent_id].specialization,
                            dependencies=[task.id]
                        )
                        logger.info(f"Created coordination task {coord_task_id} for rule: {rule['rule']}")
    
    def update_task_progress(self, task_id: str, progress: int, result: Optional[Dict[str, Any]] = None):
        '''Update task progress'''
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        task.progress = min(100, max(0, progress))
        
        if result:
            task.result = result
        
        if progress >= 100:
            self.complete_task(task_id)
        elif task.status == TaskStatus.ASSIGNED:
            task.status = TaskStatus.IN_PROGRESS
        
        logger.info(f"Updated task {task_id} progress to {progress}%")
        return True
    
    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None):
        '''Mark task as completed'''
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.status = TaskStatus.COMPLETED
        task.progress = 100

        if result:
            task.result = result

        # Remove from agent's current tasks
        if task.assigned_agent:
            agent = self.agents.get(task.assigned_agent)
            if agent and task_id in agent.current_tasks:
                agent.current_tasks.remove(task_id)

                # Update agent performance
                self._update_agent_performance(agent, task)

        logger.info(f"Completed task: {task.title}")

        # Check for dependent tasks
        self._check_dependent_tasks(task_id)

        return True

    def cancel_task(self, task_id: str, reason: Optional[str] = None) -> bool:
        '''Cancel a task'''
        task = self.tasks.get(task_id)
        if not task:
            return False

        # Cannot cancel already completed tasks
        if task.status == TaskStatus.COMPLETED:
            logger.warning(f"Cannot cancel completed task: {task_id}")
            return False

        # Remove from agent's current tasks if assigned
        if task.assigned_agent:
            agent = self.agents.get(task.assigned_agent)
            if agent and task_id in agent.current_tasks:
                agent.current_tasks.remove(task_id)

        # Remove from task queue if pending
        if task_id in self.task_queue.get(task.priority, []):
            self.task_queue[task.priority].remove(task_id)

        # Update task status
        task.status = TaskStatus.CANCELLED
        if reason:
            task.result = {'cancellation_reason': reason}

        logger.info(f"Cancelled task: {task.title} (ID: {task_id})")
        return True

    def delete_task(self, task_id: str) -> bool:
        '''Delete a task completely from the system'''
        task = self.tasks.get(task_id)
        if not task:
            return False

        # Remove from agent's current tasks if assigned
        if task.assigned_agent:
            agent = self.agents.get(task.assigned_agent)
            if agent and task_id in agent.current_tasks:
                agent.current_tasks.remove(task_id)

        # Remove from task queue if pending
        if task_id in self.task_queue.get(task.priority, []):
            self.task_queue[task.priority].remove(task_id)

        # Remove task from tasks dict
        del self.tasks[task_id]

        logger.info(f"Deleted task: {task.title} (ID: {task_id})")
        return True

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> bool:
        '''Update task status to a specific value'''
        task = self.tasks.get(task_id)
        if not task:
            return False

        old_status = task.status

        # Handle transitions that need cleanup
        if new_status in [TaskStatus.CANCELLED, TaskStatus.FAILED]:
            # Remove from agent's current tasks if assigned
            if task.assigned_agent:
                agent = self.agents.get(task.assigned_agent)
                if agent and task_id in agent.current_tasks:
                    agent.current_tasks.remove(task_id)

            # Remove from task queue if pending
            if task_id in self.task_queue.get(task.priority, []):
                self.task_queue[task.priority].remove(task_id)

        elif new_status == TaskStatus.COMPLETED:
            task.progress = 100
            # Remove from agent's current tasks
            if task.assigned_agent:
                agent = self.agents.get(task.assigned_agent)
                if agent and task_id in agent.current_tasks:
                    agent.current_tasks.remove(task_id)
                    self._update_agent_performance(agent, task)
            # Check for dependent tasks
            self._check_dependent_tasks(task_id)

        elif new_status == TaskStatus.PENDING:
            # Reset assignment and add back to queue if not already there
            task.assigned_agent = None
            task.progress = 0
            if task_id not in self.task_queue.get(task.priority, []):
                self.task_queue[task.priority].append(task_id)

        task.status = new_status
        logger.info(f"Updated task {task_id} status from {old_status.value} to {new_status.value}")
        return True
    
    def _update_agent_performance(self, agent: Agent, task: Task):
        '''Update agent performance based on task completion'''
        # Simple performance calculation - could be enhanced
        completion_time = datetime.now() - task.created_at
        
        if task.deadline:
            if completion_time <= (task.deadline - task.created_at):
                # Completed on time - boost performance
                agent.performance_score = min(2.0, agent.performance_score * 1.05)
            else:
                # Late completion - reduce performance
                agent.performance_score = max(0.1, agent.performance_score * 0.95)
        else:
            # No deadline - small boost for completion
            agent.performance_score = min(2.0, agent.performance_score * 1.01)
        
        logger.info(f"Updated {agent.name} performance to {agent.performance_score:.2f}")
    
    def _check_dependent_tasks(self, completed_task_id: str):
        '''Check and potentially assign tasks that were waiting for this one'''
        for task in self.tasks.values():
            if (completed_task_id in task.dependencies and 
                task.status == TaskStatus.PENDING and
                self._check_dependencies(task)):
                self._assign_task(task.id)
    
    def start_task_processor(self):
        '''Start the automated task processing system'''
        if self.running:
            return
        
        self.running = True
        threading.Thread(target=self._task_processor_loop, daemon=True).start()
        logger.info("Started automated task processor")
    
    def _task_processor_loop(self):
        '''Main task processing loop'''
        while self.running:
            try:
                # Process tasks by priority
                for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, 
                               TaskPriority.MEDIUM, TaskPriority.LOW]:
                    queue = self.task_queue[priority]
                    
                    # Try to assign pending tasks
                    for task_id in queue.copy():
                        if self._assign_task(task_id):
                            break  # Assigned one task, move to next priority
                
                # Check for stuck or overdue tasks
                self._check_stuck_tasks()
                
                # Update performance metrics
                self._update_performance_metrics()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in task processor loop: {e}")
                time.sleep(60)
    
    def _check_stuck_tasks(self):
        '''Check for tasks that might be stuck'''
        current_time = datetime.now()
        
        for task in self.tasks.values():
            if task.status == TaskStatus.IN_PROGRESS:
                # Check if task has been in progress too long
                if task.assigned_agent:
                    agent = self.agents.get(task.assigned_agent)
                    if agent:
                        time_since_active = current_time - agent.last_active
                        
                        # If agent hasn't been active for 1 hour, reassign task
                        if time_since_active > timedelta(hours=1):
                            logger.warning(f"Reassigning stuck task {task.id} from inactive agent {agent.name}")
                            self._reassign_task(task.id)
    
    def _reassign_task(self, task_id: str):
        '''Reassign a task to a different agent'''
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        # Remove from current agent
        if task.assigned_agent:
            agent = self.agents.get(task.assigned_agent)
            if agent and task_id in agent.current_tasks:
                agent.current_tasks.remove(task_id)
        
        # Reset task status
        task.assigned_agent = None
        task.status = TaskStatus.PENDING
        task.progress = 0
        
        # Add back to queue
        self.task_queue[task.priority].append(task_id)
        
        logger.info(f"Reset task {task_id} for reassignment")
        return True
    
    def _update_performance_metrics(self):
        '''Update system performance metrics'''
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        
        self.performance_metrics = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completion_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
            'agent_utilization': {
                agent_id: len(agent.current_tasks) / agent.max_concurrent_tasks
                for agent_id, agent in self.agents.items()
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        '''Get detailed task status'''
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return asdict(task)
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        '''Get detailed agent status'''
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        return asdict(agent)
    
    def get_system_status(self) -> Dict[str, Any]:
        '''Get overall system status'''
        return {
            'agents': {agent_id: asdict(agent) for agent_id, agent in self.agents.items()},
            'task_queue_lengths': {
                priority.value: len(queue) for priority, queue in self.task_queue.items()
            },
            'performance_metrics': self.performance_metrics,
            'running': self.running
        }

# Global task manager instance
task_manager = TaskManager()

# Example usage and testing
if __name__ == "__main__":
    # Start the task processor
    task_manager.start_task_processor()
    
    # Create some example tasks
    task1 = task_manager.create_task(
        title="Monitor DAO Proposals",
        description="Monitor and analyze new DAO governance proposals",
        priority=TaskPriority.HIGH,
        specialization=AgentSpecialization.GOVERNANCE,
        estimated_duration=60
    )
    
    task2 = task_manager.create_task(
        title="Optimize DeFi Yields",
        description="Analyze and optimize current DeFi yield strategies",
        priority=TaskPriority.MEDIUM,
        specialization=AgentSpecialization.DEFI,
        estimated_duration=120
    )
    
    task3 = task_manager.create_task(
        title="Security Audit",
        description="Perform security audit of smart contracts",
        priority=TaskPriority.CRITICAL,
        specialization=AgentSpecialization.SECURITY,
        estimated_duration=180
    )
    
    print("Task management system initialized with example tasks")
    print(f"System status: {task_manager.get_system_status()}")
