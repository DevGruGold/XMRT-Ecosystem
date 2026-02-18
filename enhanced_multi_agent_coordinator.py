#!/usr/bin/env python3
"""
XMRT-Ecosystem: Enhanced Multi-Agent Coordinator v2.0
Advanced orchestration with intelligent task delegation, load balancing, and autonomous learning

Features:
- Advanced priority queue management
- Dynamic load balancing across agents
- Intelligent task delegation based on agent capabilities
- Real-time performance monitoring and optimization
- Cross-agent communication and coordination
- Adaptive learning from task outcomes
- Predictive resource allocation
- Fault tolerance and recovery mechanisms
"""

import asyncio
import logging
import threading
import json
import time
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum, IntEnum
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import heapq
import concurrent.futures
from contextlib import asynccontextmanager
from xmrt_coordination_core import AgentMessage, MessageType

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskPriority(IntEnum):
    """Enhanced task priority with numerical ordering"""
    LOW = 1
    MEDIUM = 2  
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class TaskType(Enum):
    """Comprehensive task categorization"""
    ANALYSIS = "analysis"
    DEVELOPMENT = "development"
    MONITORING = "monitoring"
    SECURITY = "security"
    COORDINATION = "coordination"
    RESEARCH = "research"
    OPTIMIZATION = "optimization"
    COMMUNICATION = "communication"
    LEARNING = "learning"
    EMERGENCY = "emergency"

class AgentStatus(Enum):
    """Agent operational states"""
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"

class TaskStatus(Enum):
    """Task lifecycle states"""
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DELEGATED = "delegated"

@dataclass
class AgentCapability:
    """Enhanced agent capability with performance tracking"""
    name: str
    proficiency: float  # 0.0 - 1.0
    experience_count: int = 0
    success_rate: float = 1.0
    avg_completion_time: float = 0.0
    reliability_score: float = 1.0
    learning_rate: float = 0.1
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def update_performance(self, success: bool, completion_time: float):
        """Update capability performance metrics"""
        self.experience_count += 1

        # Update success rate with exponential moving average
        alpha = 0.1
        if success:
            self.success_rate = (1 - alpha) * self.success_rate + alpha * 1.0
        else:
            self.success_rate = (1 - alpha) * self.success_rate + alpha * 0.0

        # Update average completion time
        if self.avg_completion_time == 0:
            self.avg_completion_time = completion_time
        else:
            self.avg_completion_time = (1 - alpha) * self.avg_completion_time + alpha * completion_time

        # Calculate reliability score
        self.reliability_score = min(1.0, self.success_rate * (1.0 / max(1.0, self.avg_completion_time / 10.0)))
        self.last_updated = datetime.utcnow()

@dataclass
class EnhancedTask:
    """Comprehensive task definition with advanced metadata"""
    id: str
    type: TaskType
    priority: TaskPriority
    description: str
    required_capabilities: List[str]
    estimated_duration: float
    max_retries: int = 3
    retry_count: int = 0
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.QUEUED
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def __lt__(self, other):
        """Support priority queue ordering"""
        # Higher priority values come first (reversed for min-heap)
        return self.priority.value > other.priority.value

    @property
    def age(self) -> float:
        """Task age in seconds"""
        return (datetime.utcnow() - self.created_at).total_seconds()

    @property
    def is_overdue(self) -> bool:
        """Check if task has exceeded estimated duration"""
        if self.start_time is None:
            return False
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        return elapsed > self.estimated_duration * 1.5

@dataclass
class AgentPerformanceMetrics:
    """Comprehensive agent performance tracking"""
    agent_id: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    current_load: int = 0
    max_concurrent_tasks: int = 3
    capabilities: Dict[str, AgentCapability] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    stress_level: float = 0.0  # 0.0 - 1.0

    @property
    def success_rate(self) -> float:
        """Overall agent success rate"""
        total = self.tasks_completed + self.tasks_failed
        return self.tasks_completed / total if total > 0 else 1.0

    @property
    def average_processing_time(self) -> float:
        """Average task processing time"""
        return self.total_processing_time / self.tasks_completed if self.tasks_completed > 0 else 0.0

    @property
    def efficiency_score(self) -> float:
        """Combined efficiency metric"""
        return self.success_rate * (1.0 - min(1.0, self.stress_level)) * (1.0 / max(1.0, self.average_processing_time / 10.0))

class MessageBus:
    """
    Asynchronous Message Bus for Inter-Agent Communication
    Enables structured A2A messaging with subscription support.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[AgentMessage], Any]]] = defaultdict(list)
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._processing_task = None
        logger.info("🚌 A2A Message Bus initialized")

    async def start(self):
        """Start the message processing loop"""
        if self._running:
            return
        self._running = True
        self._processing_task = asyncio.create_task(self._process_messages())
        logger.info("🚀 Message Bus started")

    async def stop(self):
        """Stop the message processing loop"""
        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Message Bus stopped")

    def subscribe(self, receiver_id: str, callback: Callable[[AgentMessage], Any]):
        """Subscribe an agent to messages addressed to them"""
        self._subscribers[receiver_id].append(callback)
        logger.info(f"📝 Agent {receiver_id} subscribed to message bus")

    async def post_message(self, message: AgentMessage):
        """Post a message to the bus"""
        await self._message_queue.put(message)
        logger.debug(f"📨 Message {message.id} posted from {message.sender} to {message.receiver}")

    async def _process_messages(self):
        """Internal loop to distribute messages"""
        while self._running:
            try:
                message = await self._message_queue.get()
                receiver = message.receiver
                
                # Deliver to specific subscribers
                if receiver in self._subscribers:
                    for callback in self._subscribers[receiver]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                asyncio.create_task(callback(message))
                            else:
                                callback(message)
                        except Exception as e:
                            logger.error(f"Error delivering message {message.id} to {receiver}: {e}")
                
                # Broadcast support (if receiver is 'all' or 'broadcast')
                if receiver in ['all', 'broadcast'] and message.receiver != 'all':
                     # Prevent infinite loops if logic changes, but for now simple check
                     pass

                self._message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message processing loop: {e}")

class EnhancedMultiAgentCoordinator:
    """
    Advanced Multi-Agent Coordinator with intelligent orchestration

    Features:
    - Priority-based task queuing with dynamic reordering
    - Intelligent agent selection based on capabilities and load
    - Real-time performance monitoring and optimization
    - Adaptive load balancing and resource allocation
    - Cross-agent communication and coordination
    - Fault tolerance and automatic recovery
    - Learning from task outcomes and agent performance
    """

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.task_queue = []  # Priority queue
        self.active_tasks: Dict[str, EnhancedTask] = {}
        self.completed_tasks: deque = deque(maxlen=1000)
        self.agent_metrics: Dict[str, AgentPerformanceMetrics] = {}
        self.task_history: List[Dict[str, Any]] = []

        # Coordination state
        self.coordinator_lock = asyncio.Lock()
        self.running = False
        self.coordination_interval = 5.0  # seconds
        self.learning_interval = 30.0  # seconds

        # Performance tracking
        self.system_metrics = {
            'total_tasks_processed': 0,
            'average_queue_time': 0.0,
            'system_throughput': 0.0,
            'load_balance_efficiency': 1.0,
            'coordination_overhead': 0.0
        }

        # Event handlers
        self.task_handlers: Dict[TaskType, Callable] = {}
        self.event_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Message Bus
        self.message_bus = MessageBus()

        logger.info("🤖 Enhanced Multi-Agent Coordinator initialized")

    async def start(self):
        """Start the coordination system"""
        self.running = True
        
        # Start Message Bus
        await self.message_bus.start()

        # Start background processes
        coordination_task = asyncio.create_task(self._coordination_loop())
        learning_task = asyncio.create_task(self._learning_loop())
        monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info("🚀 Enhanced Multi-Agent Coordinator started")

        # Return tasks for external management if needed
        return [coordination_task, learning_task, monitoring_task]

    async def stop(self):
        """Gracefully stop the coordination system"""
        self.running = False
        await self.message_bus.stop()
        logger.info("⏹️ Enhanced Multi-Agent Coordinator stopping...")

    def register_agent(self, agent_id: str, capabilities: List[str], max_concurrent: int = 3, message_callback: Callable = None):
        """Register a new agent with the coordinator"""
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentPerformanceMetrics(
                agent_id=agent_id,
                max_concurrent_tasks=max_concurrent
            )

            # Initialize capabilities
            for cap in capabilities:
                self.agent_metrics[agent_id].capabilities[cap] = AgentCapability(
                    name=cap,
                    proficiency=0.8  # Default proficiency
                )
            
            # Subscribe agent to message bus if callback provided
            if message_callback:
                self.message_bus.subscribe(agent_id, message_callback)
            
            logger.info(f"✅ Agent {agent_id} registered with capabilities: {capabilities}")

    def register_task_handler(self, task_type: TaskType, handler: Callable):
        """Register a handler function for a specific task type"""
        self.task_handlers[task_type] = handler
        logger.info(f"📝 Handler registered for {task_type.value} tasks")

    def add_event_callback(self, event_type: str, callback: Callable):
        """Add callback for system events"""
        self.event_callbacks[event_type].append(callback)

    async def submit_task(self, task: EnhancedTask) -> str:
        """Submit a new task to the coordination system"""
        async with self.coordinator_lock:
            heapq.heappush(self.task_queue, task)
            self.system_metrics['total_tasks_processed'] += 1

            # Trigger immediate coordination if system is idle
            if len(self.active_tasks) == 0:
                asyncio.create_task(self._coordinate_tasks())

            await self._emit_event('task_submitted', {'task_id': task.id, 'type': task.type.value})
            logger.info(f"📥 Task {task.id} submitted: {task.description[:50]}...")

        return task.id

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific task"""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                'id': task.id,
                'status': task.status.value,
                'progress': self._calculate_task_progress(task),
                'assigned_agent': task.assigned_agent,
                'created_at': task.created_at.isoformat(),
                'estimated_completion': self._estimate_completion_time(task)
            }

        # Check completed tasks
        for task_data in self.completed_tasks:
            if task_data.get('id') == task_id:
                return task_data

        return None

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        active_agents = sum(1 for metrics in self.agent_metrics.values() 
                          if (datetime.utcnow() - metrics.last_heartbeat).total_seconds() < 60)

        return {
            'status': 'running' if self.running else 'stopped',
            'active_agents': active_agents,
            'total_agents': len(self.agent_metrics),
            'queued_tasks': len(self.task_queue),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'system_metrics': self.system_metrics.copy(),
            'agent_performance': {
                agent_id: {
                    'success_rate': metrics.success_rate,
                    'efficiency_score': metrics.efficiency_score,
                    'current_load': metrics.current_load,
                    'stress_level': metrics.stress_level
                }
                for agent_id, metrics in self.agent_metrics.items()
            }
        }

    def _select_best_agent(self, task: EnhancedTask) -> Optional[str]:
        """Intelligent agent selection based on capabilities, load, and performance"""
        available_agents = []

        for agent_id, metrics in self.agent_metrics.items():
            # Check if agent is available and capable
            if (metrics.current_load < metrics.max_concurrent_tasks and 
                (datetime.utcnow() - metrics.last_heartbeat).total_seconds() < 60):

                # Calculate capability score
                capability_score = 0.0
                for req_cap in task.required_capabilities:
                    if req_cap in metrics.capabilities:
                        cap = metrics.capabilities[req_cap]
                        capability_score += cap.proficiency * cap.reliability_score

                if capability_score > 0:
                    # Calculate overall agent score
                    load_factor = 1.0 - (metrics.current_load / metrics.max_concurrent_tasks)
                    performance_factor = metrics.efficiency_score
                    stress_factor = 1.0 - metrics.stress_level

                    total_score = capability_score * load_factor * performance_factor * stress_factor

                    available_agents.append((agent_id, total_score))

        if available_agents:
            # Sort by score and return best agent
            available_agents.sort(key=lambda x: x[1], reverse=True)
            return available_agents[0][0]

        return None

    async def _coordinate_tasks(self):
        """Main coordination logic for task assignment"""
        async with self.coordinator_lock:
            while self.task_queue and len(self.active_tasks) < self.max_workers:
                task = heapq.heappop(self.task_queue)

                # Check if task has unmet dependencies
                if self._has_unmet_dependencies(task):
                    # Re-queue for later
                    heapq.heappush(self.task_queue, task)
                    break

                # Select best agent for the task
                selected_agent = self._select_best_agent(task)

                if selected_agent:
                    # Assign task to agent
                    task.assigned_agent = selected_agent
                    task.status = TaskStatus.ASSIGNED
                    task.start_time = datetime.utcnow()

                    self.active_tasks[task.id] = task
                    self.agent_metrics[selected_agent].current_load += 1

                    # Execute task asynchronously
                    asyncio.create_task(self._execute_task(task))

                    await self._emit_event('task_assigned', {
                        'task_id': task.id,
                        'agent_id': selected_agent,
                        'priority': task.priority.value
                    })

                    logger.info(f"🎯 Task {task.id} assigned to agent {selected_agent}")
                else:
                    # No suitable agent available, re-queue
                    heapq.heappush(self.task_queue, task)
                    break

    async def _execute_task(self, task: EnhancedTask):
        """Execute a task with comprehensive error handling and monitoring"""
        start_time = time.time()

        try:
            task.status = TaskStatus.IN_PROGRESS

            # Get task handler
            handler = self.task_handlers.get(task.type)
            if not handler:
                raise Exception(f"No handler registered for task type: {task.type.value}")

            # Execute the task
            if asyncio.iscoroutinefunction(handler):
                result = await handler(task)
            else:
                result = handler(task)

            # Task completed successfully
            task.status = TaskStatus.COMPLETED
            task.completion_time = datetime.utcnow()
            task.result = result

            # Update agent performance
            execution_time = time.time() - start_time
            agent_metrics = self.agent_metrics[task.assigned_agent]
            agent_metrics.tasks_completed += 1
            agent_metrics.total_processing_time += execution_time

            # Update capability performance
            for cap_name in task.required_capabilities:
                if cap_name in agent_metrics.capabilities:
                    agent_metrics.capabilities[cap_name].update_performance(True, execution_time)

            await self._emit_event('task_completed', {
                'task_id': task.id,
                'agent_id': task.assigned_agent,
                'execution_time': execution_time,
                'result_summary': str(result)[:100] if result else None
            })

            logger.info(f"✅ Task {task.id} completed by {task.assigned_agent} in {execution_time:.2f}s")

        except Exception as e:
            # Task failed
            task.status = TaskStatus.FAILED
            task.completion_time = datetime.utcnow()
            task.error_message = str(e)

            execution_time = time.time() - start_time
            agent_metrics = self.agent_metrics[task.assigned_agent]
            agent_metrics.tasks_failed += 1

            # Update capability performance (failure)
            for cap_name in task.required_capabilities:
                if cap_name in agent_metrics.capabilities:
                    agent_metrics.capabilities[cap_name].update_performance(False, execution_time)

            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.QUEUED
                task.assigned_agent = None
                task.start_time = None

                # Re-queue with potentially lower priority
                if task.priority.value > TaskPriority.LOW.value:
                    task.priority = TaskPriority(task.priority.value - 1)

                async with self.coordinator_lock:
                    heapq.heappush(self.task_queue, task)

                logger.warning(f"🔄 Task {task.id} failed, retrying (attempt {task.retry_count}/{task.max_retries})")
            else:
                await self._emit_event('task_failed', {
                    'task_id': task.id,
                    'agent_id': task.assigned_agent,
                    'error': task.error_message,
                    'execution_time': execution_time
                })

                logger.error(f"❌ Task {task.id} failed permanently: {task.error_message}")

        finally:
            # Clean up
            if task.assigned_agent:
                self.agent_metrics[task.assigned_agent].current_load -= 1

            if task.id in self.active_tasks:
                completed_task = self.active_tasks.pop(task.id)
                self.completed_tasks.append({
                    'id': completed_task.id,
                    'type': completed_task.type.value,
                    'status': completed_task.status.value,
                    'created_at': completed_task.created_at.isoformat(),
                    'completion_time': completed_task.completion_time.isoformat() if completed_task.completion_time else None,
                    'assigned_agent': completed_task.assigned_agent,
                    'execution_time': (completed_task.completion_time - completed_task.start_time).total_seconds() if completed_task.completion_time and completed_task.start_time else None,
                    'result': completed_task.result,
                    'error': completed_task.error_message
                })

            # Trigger next coordination cycle
            if self.running:
                asyncio.create_task(self._coordinate_tasks())

    def _has_unmet_dependencies(self, task: EnhancedTask) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_id in task.dependencies:
            # Check if dependency is completed
            dependency_completed = False
            for completed_task in self.completed_tasks:
                if completed_task.get('id') == dep_id and completed_task.get('status') == 'completed':
                    dependency_completed = True
                    break

            if not dependency_completed:
                return True

        return False

    def _calculate_task_progress(self, task: EnhancedTask) -> float:
        """Estimate task progress based on elapsed time and estimated duration"""
        if task.status == TaskStatus.COMPLETED:
            return 1.0
        elif task.status in [TaskStatus.QUEUED, TaskStatus.ASSIGNED]:
            return 0.0
        elif task.status == TaskStatus.IN_PROGRESS and task.start_time:
            elapsed = (datetime.utcnow() - task.start_time).total_seconds()
            return min(0.95, elapsed / task.estimated_duration)  # Cap at 95% until completion

        return 0.0

    def _estimate_completion_time(self, task: EnhancedTask) -> Optional[str]:
        """Estimate when a task will be completed"""
        if task.status == TaskStatus.COMPLETED:
            return task.completion_time.isoformat() if task.completion_time else None
        elif task.status == TaskStatus.IN_PROGRESS and task.start_time:
            estimated_end = task.start_time + timedelta(seconds=task.estimated_duration)
            return estimated_end.isoformat()
        elif task.status in [TaskStatus.QUEUED, TaskStatus.ASSIGNED]:
            # Estimate based on queue position and agent availability
            queue_time = len(self.task_queue) * 10.0  # Rough estimate
            estimated_start = datetime.utcnow() + timedelta(seconds=queue_time)
            estimated_end = estimated_start + timedelta(seconds=task.estimated_duration)
            return estimated_end.isoformat()

        return None

    async def _coordination_loop(self):
        """Background coordination loop"""
        while self.running:
            try:
                await self._coordinate_tasks()
                await self._update_agent_stress_levels()
                await self._rebalance_loads()

                await asyncio.sleep(self.coordination_interval)

            except Exception as e:
                logger.error(f"Coordination loop error: {e}")
                await asyncio.sleep(1.0)

    async def _learning_loop(self):
        """Background learning and optimization loop"""
        while self.running:
            try:
                await self._analyze_performance_patterns()
                await self._optimize_task_scheduling()
                await self._update_capability_estimates()

                await asyncio.sleep(self.learning_interval)

            except Exception as e:
                logger.error(f"Learning loop error: {e}")
                await asyncio.sleep(5.0)

    async def _monitoring_loop(self):
        """Background system monitoring loop"""
        while self.running:
            try:
                await self._check_agent_health()
                await self._detect_performance_anomalies()
                await self._cleanup_stale_tasks()

                await asyncio.sleep(10.0)

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(2.0)

    async def _update_agent_stress_levels(self):
        """Calculate and update agent stress levels"""
        for agent_id, metrics in self.agent_metrics.items():
            load_ratio = metrics.current_load / metrics.max_concurrent_tasks
            failure_rate = metrics.tasks_failed / max(1, metrics.tasks_completed + metrics.tasks_failed)

            # Calculate stress based on load and performance
            stress = min(1.0, load_ratio * 0.7 + failure_rate * 0.3)
            metrics.stress_level = stress

    async def _rebalance_loads(self):
        """Implement intelligent load balancing"""
        # Find overloaded and underutilized agents
        overloaded = [(aid, metrics) for aid, metrics in self.agent_metrics.items() 
                     if metrics.stress_level > 0.8]
        underutilized = [(aid, metrics) for aid, metrics in self.agent_metrics.items() 
                        if metrics.stress_level < 0.3 and metrics.current_load < metrics.max_concurrent_tasks]

        # Implement task migration logic if needed
        if overloaded and underutilized:
            logger.info(f"🔄 Load balancing: {len(overloaded)} overloaded, {len(underutilized)} underutilized agents")

    async def _analyze_performance_patterns(self):
        """Analyze system performance and identify optimization opportunities"""
        if len(self.completed_tasks) < 10:
            return

        # Calculate system-wide metrics
        total_tasks = len(self.completed_tasks)
        successful_tasks = sum(1 for task in self.completed_tasks if task.get('status') == 'completed')

        if total_tasks > 0:
            system_success_rate = successful_tasks / total_tasks
            self.system_metrics['system_success_rate'] = system_success_rate

            # Calculate average execution times by task type
            task_type_metrics = defaultdict(list)
            for task in self.completed_tasks:
                if task.get('execution_time'):
                    task_type_metrics[task.get('type', 'unknown')].append(task['execution_time'])

            # Update estimates
            for task_type, times in task_type_metrics.items():
                if times:
                    avg_time = np.mean(times)
                    self.system_metrics[f'avg_time_{task_type}'] = avg_time

    async def _optimize_task_scheduling(self):
        """Optimize task scheduling based on historical performance"""
        # Implement dynamic priority adjustment based on success patterns
        # This could include machine learning models for better predictions
        pass

    async def _update_capability_estimates(self):
        """Update agent capability estimates based on recent performance"""
        for agent_id, metrics in self.agent_metrics.items():
            for cap_name, capability in metrics.capabilities.items():
                # Decay old performance data slightly
                if capability.experience_count > 0:
                    decay_factor = 0.99
                    capability.success_rate *= decay_factor
                    capability.reliability_score *= decay_factor

    async def _check_agent_health(self):
        """Monitor agent health and detect issues"""
        current_time = datetime.utcnow()

        for agent_id, metrics in self.agent_metrics.items():
            time_since_heartbeat = (current_time - metrics.last_heartbeat).total_seconds()

            if time_since_heartbeat > 120:  # 2 minutes without heartbeat
                logger.warning(f"⚠️ Agent {agent_id} appears offline (last heartbeat: {time_since_heartbeat:.0f}s ago)")

                # Move tasks back to queue if agent is unresponsive
                tasks_to_requeue = [task for task in self.active_tasks.values() 
                                  if task.assigned_agent == agent_id]

                for task in tasks_to_requeue:
                    task.status = TaskStatus.QUEUED
                    task.assigned_agent = None
                    task.retry_count += 1

                    async with self.coordinator_lock:
                        heapq.heappush(self.task_queue, task)
                        self.active_tasks.pop(task.id, None)

    async def _detect_performance_anomalies(self):
        """Detect and respond to performance anomalies"""
        # Check for unusual patterns in task execution
        if len(self.completed_tasks) < 20:
            return

        recent_tasks = list(self.completed_tasks)[-20:]
        recent_success_rate = sum(1 for task in recent_tasks if task.get('status') == 'completed') / len(recent_tasks)

        if recent_success_rate < 0.5:
            logger.warning(f"⚠️ Performance anomaly detected: Recent success rate {recent_success_rate:.2%}")
            await self._emit_event('performance_anomaly', {'success_rate': recent_success_rate})

    async def _cleanup_stale_tasks(self):
        """Clean up stale or abandoned tasks"""
        current_time = datetime.utcnow()

        stale_tasks = []
        for task_id, task in self.active_tasks.items():
            if task.is_overdue:
                stale_tasks.append(task)

        for task in stale_tasks:
            logger.warning(f"🧹 Cleaning up stale task {task.id}")
            task.status = TaskStatus.FAILED
            task.error_message = "Task exceeded maximum execution time"

            if task.assigned_agent:
                self.agent_metrics[task.assigned_agent].current_load -= 1

            self.active_tasks.pop(task.id, None)

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit system events to registered callbacks"""
        try:
            callbacks = self.event_callbacks.get(event_type, [])
            for callback in callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
        except Exception as e:
            logger.error(f"Error emitting event {event_type}: {e}")

# Convenience functions for task creation
def create_analysis_task(description: str, priority: TaskPriority = TaskPriority.MEDIUM, 
                        estimated_duration: float = 30.0) -> EnhancedTask:
    """Create an analysis task"""
    return EnhancedTask(
        id=str(uuid.uuid4()),
        type=TaskType.ANALYSIS,
        priority=priority,
        description=description,
        required_capabilities=['analysis', 'data_processing'],
        estimated_duration=estimated_duration
    )

def create_development_task(description: str, priority: TaskPriority = TaskPriority.HIGH,
                           estimated_duration: float = 120.0) -> EnhancedTask:
    """Create a development task"""
    return EnhancedTask(
        id=str(uuid.uuid4()),
        type=TaskType.DEVELOPMENT,
        priority=priority,
        description=description,
        required_capabilities=['coding', 'development', 'testing'],
        estimated_duration=estimated_duration
    )

def create_security_task(description: str, priority: TaskPriority = TaskPriority.HIGH,
                        estimated_duration: float = 60.0) -> EnhancedTask:
    """Create a security task"""
    return EnhancedTask(
        id=str(uuid.uuid4()),
        type=TaskType.SECURITY,
        priority=priority,
        description=description,
        required_capabilities=['security', 'vulnerability_scanning', 'threat_detection'],
        estimated_duration=estimated_duration
    )

# Example usage and integration
async def main():
    """Example usage of the Enhanced Multi-Agent Coordinator"""

    # Initialize coordinator
    coordinator = EnhancedMultiAgentCoordinator(max_workers=5)

    # Register agents
    coordinator.register_agent('eliza', ['analysis', 'coordination', 'github_integration'], max_concurrent=2)
    coordinator.register_agent('defi_specialist', ['analysis', 'financial_modeling', 'data_processing'], max_concurrent=3)
    coordinator.register_agent('security_guardian', ['security', 'vulnerability_scanning', 'threat_detection'], max_concurrent=2)

    # Register task handlers (these would be implemented elsewhere)
    async def analysis_handler(task):
        await asyncio.sleep(2)  # Simulate work
        return {'analysis_complete': True, 'insights': ['insight1', 'insight2']}

    coordinator.register_task_handler(TaskType.ANALYSIS, analysis_handler)

    # Start the coordinator
    await coordinator.start()

    # Submit some tasks
    task1 = create_analysis_task("Analyze repository health", TaskPriority.HIGH)
    task2 = create_security_task("Scan for vulnerabilities", TaskPriority.CRITICAL)

    await coordinator.submit_task(task1)
    await coordinator.submit_task(task2)

    # Monitor for a while
    await asyncio.sleep(10)

    # Get system status
    status = await coordinator.get_system_status()
    print(json.dumps(status, indent=2))

    await coordinator.stop()

if __name__ == "__main__":
    asyncio.run(main())
