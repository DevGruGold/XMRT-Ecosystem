#!/usr/bin/env python3
'''
XMRT Ecosystem Agent Coordination API
Provides REST API endpoints for task management and agent coordination
'''

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from task_manager import task_manager, TaskPriority, AgentSpecialization, TaskStatus
import logging

logger = logging.getLogger(__name__)

# Create Blueprint for coordination API
coordination_bp = Blueprint('coordination', __name__, url_prefix='/api/coordination')

@coordination_bp.route('/tasks', methods=['GET'])
def get_tasks():
    '''Get all tasks with optional filtering'''
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    agent_filter = request.args.get('agent')
    
    tasks = []
    for task in task_manager.tasks.values():
        # Apply filters
        if status_filter and task.status.value != status_filter:
            continue
        if priority_filter and task.priority.value != priority_filter:
            continue
        if agent_filter and task.assigned_agent != agent_filter:
            continue
        
        task_dict = task_manager.get_task_status(task.id)
        if task_dict:
            # Convert datetime objects to ISO strings
            if 'created_at' in task_dict and task_dict['created_at']:
                task_dict['created_at'] = task_dict['created_at'].isoformat()
            if 'deadline' in task_dict and task_dict['deadline']:
                task_dict['deadline'] = task_dict['deadline'].isoformat()
            
            tasks.append(task_dict)
    
    return jsonify({
        'tasks': tasks,
        'total': len(tasks),
        'filters_applied': {
            'status': status_filter,
            'priority': priority_filter,
            'agent': agent_filter
        }
    })

@coordination_bp.route('/tasks', methods=['POST'])
def create_task():
    '''Create a new task'''
    data = request.get_json()
    
    required_fields = ['title', 'description', 'priority', 'specialization']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        priority = TaskPriority(data['priority'])
        specialization = AgentSpecialization(data['specialization'])
        
        deadline = None
        if 'deadline' in data:
            deadline = datetime.fromisoformat(data['deadline'])
        
        dependencies = data.get('dependencies', [])
        estimated_duration = data.get('estimated_duration')
        
        task_id = task_manager.create_task(
            title=data['title'],
            description=data['description'],
            priority=priority,
            specialization=specialization,
            deadline=deadline,
            dependencies=dependencies,
            estimated_duration=estimated_duration
        )
        
        return jsonify({
            'task_id': task_id,
            'message': 'Task created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid value: {e}'}), 400
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@coordination_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    '''Get specific task details'''
    task_status = task_manager.get_task_status(task_id)
    
    if not task_status:
        return jsonify({'error': 'Task not found'}), 404
    
    # Convert datetime objects to ISO strings
    if 'created_at' in task_status and task_status['created_at']:
        task_status['created_at'] = task_status['created_at'].isoformat()
    if 'deadline' in task_status and task_status['deadline']:
        task_status['deadline'] = task_status['deadline'].isoformat()
    
    return jsonify(task_status)

@coordination_bp.route('/tasks/<task_id>/progress', methods=['PUT'])
def update_task_progress(task_id):
    '''Update task progress'''
    data = request.get_json()
    
    if 'progress' not in data:
        return jsonify({'error': 'Progress value required'}), 400
    
    try:
        progress = int(data['progress'])
        result = data.get('result')
        
        success = task_manager.update_task_progress(task_id, progress, result)
        
        if success:
            return jsonify({'message': 'Progress updated successfully'})
        else:
            return jsonify({'error': 'Task not found'}), 404
            
    except ValueError:
        return jsonify({'error': 'Progress must be an integer'}), 400
    except Exception as e:
        logger.error(f"Error updating task progress: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@coordination_bp.route('/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    '''Mark task as completed'''
    data = request.get_json() or {}
    result = data.get('result')

    success = task_manager.complete_task(task_id, result)

    if success:
        return jsonify({'message': 'Task completed successfully'})
    else:
        return jsonify({'error': 'Task not found'}), 404

@coordination_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    '''Cancel a task'''
    data = request.get_json() or {}
    reason = data.get('reason')

    success = task_manager.cancel_task(task_id, reason)

    if success:
        return jsonify({'message': 'Task cancelled successfully'})
    else:
        return jsonify({'error': 'Task not found or cannot be cancelled'}), 404

@coordination_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    '''Delete a task'''
    success = task_manager.delete_task(task_id)

    if success:
        return jsonify({'message': 'Task deleted successfully'})
    else:
        return jsonify({'error': 'Task not found'}), 404

@coordination_bp.route('/tasks/<task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    '''Update task status'''
    data = request.get_json()

    if 'status' not in data:
        return jsonify({'error': 'Status value required'}), 400

    try:
        new_status = TaskStatus(data['status'])
        success = task_manager.update_task_status(task_id, new_status)

        if success:
            return jsonify({'message': f'Task status updated to {new_status.value}'})
        else:
            return jsonify({'error': 'Task not found'}), 404

    except ValueError:
        valid_statuses = [s.value for s in TaskStatus]
        return jsonify({'error': f'Invalid status. Valid values: {valid_statuses}'}), 400
    except Exception as e:
        logger.error(f"Error updating task status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@coordination_bp.route('/agents', methods=['GET'])
def get_agents():
    '''Get all agents and their status'''
    agents = {}
    
    for agent_id, agent in task_manager.agents.items():
        agent_status = task_manager.get_agent_status(agent_id)
        if agent_status:
            # Convert datetime objects to ISO strings
            if 'last_active' in agent_status and agent_status['last_active']:
                agent_status['last_active'] = agent_status['last_active'].isoformat()
            
            agents[agent_id] = agent_status
    
    return jsonify({
        'agents': agents,
        'total': len(agents)
    })

@coordination_bp.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    '''Get specific agent details'''
    agent_status = task_manager.get_agent_status(agent_id)
    
    if not agent_status:
        return jsonify({'error': 'Agent not found'}), 404
    
    # Convert datetime objects to ISO strings
    if 'last_active' in agent_status and agent_status['last_active']:
        agent_status['last_active'] = agent_status['last_active'].isoformat()
    
    return jsonify(agent_status)

@coordination_bp.route('/system/status', methods=['GET'])
def get_system_status():
    '''Get overall system status'''
    status = task_manager.get_system_status()
    
    # Convert datetime objects in performance metrics
    if 'performance_metrics' in status and 'last_updated' in status['performance_metrics']:
        # last_updated is already in ISO format from task_manager
        pass
    
    # Convert datetime objects in agents
    if 'agents' in status:
        for agent_id, agent_data in status['agents'].items():
            if 'last_active' in agent_data and agent_data['last_active']:
                agent_data['last_active'] = agent_data['last_active'].isoformat()
    
    return jsonify(status)

@coordination_bp.route('/system/metrics', methods=['GET'])
def get_performance_metrics():
    '''Get system performance metrics'''
    return jsonify(task_manager.performance_metrics)

@coordination_bp.route('/coordination/rules', methods=['GET'])
def get_coordination_rules():
    '''Get active coordination rules'''
    rules = []
    for rule in task_manager.coordination_rules:
        rules.append({
            'rule': rule['rule'],
            'description': rule['description'],
            'required_agents': rule['required_agents']
        })
    
    return jsonify({
        'rules': rules,
        'total': len(rules)
    })

@coordination_bp.route('/emergency/reassign/<task_id>', methods=['POST'])
def emergency_reassign(task_id):
    '''Emergency reassignment of a task'''
    success = task_manager._reassign_task(task_id)
    
    if success:
        return jsonify({'message': 'Task reassigned successfully'})
    else:
        return jsonify({'error': 'Task not found or cannot be reassigned'}), 404

@coordination_bp.route('/bulk/create', methods=['POST'])
def bulk_create_tasks():
    '''Create multiple tasks in bulk'''
    data = request.get_json()
    
    if 'tasks' not in data or not isinstance(data['tasks'], list):
        return jsonify({'error': 'Tasks array required'}), 400
    
    created_tasks = []
    errors = []
    
    for i, task_data in enumerate(data['tasks']):
        try:
            required_fields = ['title', 'description', 'priority', 'specialization']
            for field in required_fields:
                if field not in task_data:
                    errors.append(f'Task {i}: Missing required field: {field}')
                    continue
            
            priority = TaskPriority(task_data['priority'])
            specialization = AgentSpecialization(task_data['specialization'])
            
            deadline = None
            if 'deadline' in task_data:
                deadline = datetime.fromisoformat(task_data['deadline'])
            
            task_id = task_manager.create_task(
                title=task_data['title'],
                description=task_data['description'],
                priority=priority,
                specialization=specialization,
                deadline=deadline,
                dependencies=task_data.get('dependencies', []),
                estimated_duration=task_data.get('estimated_duration')
            )
            
            created_tasks.append(task_id)
            
        except Exception as e:
            errors.append(f'Task {i}: {str(e)}')
    
    return jsonify({
        'created_tasks': created_tasks,
        'errors': errors,
        'total_created': len(created_tasks),
        'total_errors': len(errors)
    })

# Initialize task manager when blueprint is imported
if not task_manager.running:
    task_manager.start_task_processor()
    logger.info("Task manager started from coordination API")
