#!/usr/bin/env python3
"""
XMRT-Ecosystem Enhanced Autonomous Learning System
==================================================

Advanced Flask Application with comprehensive AI agent coordination,
real-time monitoring, blockchain integration, and autonomous learning capabilities.

Features:
- Multi-agent coordination system
- Real-time WebSocket monitoring dashboard
- Blockchain and Web3 integration
- Advanced memory and learning systems
- GitHub automation and repository management
- AI-powered code analysis and optimization
- Deployment automation and health monitoring
- Security and error handling
- Performance optimization and caching

Version: 2.0 Enhanced
Author: XMRT Ecosystem Team
License: MIT
"""

import os
import sys
import json
import logging
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import traceback

# Core Flask and Web Framework
from flask import Flask, render_template_string, jsonify, request, abort, make_response
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import eventlet

# Enhanced Async Support
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Database and Caching
import redis
from cachetools import TTLCache, LRUCache

# Monitoring and Performance
import psutil
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import structlog

# Security and Authentication
from cryptography.fernet import Fernet
import jwt
from functools import wraps

# Import our enhanced autonomous system components
try:
    from autonomous_controller import AutonomousController
    from multi_agent_system import MultiAgentSystem
    from github_manager import GitHubManager
    from memory_system import MemorySystem
    from learning_optimizer import LearningOptimizer
    from performance_analyzer import PerformanceAnalyzer
    from web3_dapp_factory import Web3DAppFactory
    from analytics_system import AnalyticsSystem
except ImportError as e:
    print(f"Warning: Some advanced modules not available: {e}")

# Enhanced Configuration Management
@dataclass
class SystemConfig:
    """Enhanced system configuration with validation"""
    secret_key: str
    github_token: str
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    redis_url: str = "redis://localhost:6379"
    debug_mode: bool = False
    max_agents: int = 10
    learning_interval: int = 300  # 5 minutes
    blockchain_enabled: bool = True
    analytics_enabled: bool = True
    security_enabled: bool = True
    
    def __post_init__(self):
        """Validate configuration"""
        if not self.secret_key:
            raise ValueError("SECRET_KEY is required")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN is required")

# Enhanced Logging Configuration
def setup_enhanced_logging():
    """Setup structured logging with multiple outputs"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

# Initialize enhanced logging
setup_enhanced_logging()
logger = structlog.get_logger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter('xmrt_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('xmrt_request_duration_seconds', 'Request latency')
AGENT_COUNT = Gauge('xmrt_active_agents', 'Number of active agents')
SYSTEM_HEALTH = Gauge('xmrt_system_health', 'System health score (0-1)')

# Enhanced JSON Encoder with datetime and complex object support
class EnhancedJSONEncoder(json.JSONEncoder):
    """Advanced JSON encoder handling various Python objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, '_asdict'):  # namedtuple
            return obj._asdict()
        return super().default(obj)

# Load configuration from environment
def load_config() -> SystemConfig:
    """Load and validate system configuration"""
    try:
        config = SystemConfig(
            secret_key=os.environ.get('SECRET_KEY', 'xmrt-ecosystem-enhanced-key-2024'),
            github_token=os.environ.get('GITHUB_TOKEN', ''),
            openai_api_key=os.environ.get('OPENAI_API_KEY', ''),
            anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY', ''),
            redis_url=os.environ.get('REDIS_URL', 'redis://localhost:6379'),
            debug_mode=os.environ.get('DEBUG', 'False').lower() == 'true',
            max_agents=int(os.environ.get('MAX_AGENTS', '10')),
            learning_interval=int(os.environ.get('LEARNING_INTERVAL', '300')),
            blockchain_enabled=os.environ.get('BLOCKCHAIN_ENABLED', 'True').lower() == 'true',
            analytics_enabled=os.environ.get('ANALYTICS_ENABLED', 'True').lower() == 'true',
            security_enabled=os.environ.get('SECURITY_ENABLED', 'True').lower() == 'true'
        )
        logger.info("Configuration loaded successfully", config=asdict(config))
        return config
    except Exception as e:
        logger.error("Failed to load configuration", error=str(e))
        raise

# Initialize configuration
config = load_config()

# Initialize Flask app with enhanced configuration
app = Flask(__name__)
app.config.update({
    'SECRET_KEY': config.secret_key,
    'JSON_ENCODER': EnhancedJSONEncoder,
    'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB max file size
    'JSONIFY_PRETTYPRINT_REGULAR': config.debug_mode,
})

# Enable CORS for cross-origin requests
CORS(app, origins=["*"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Initialize Redis cache
redis_client = None
try:
    redis_client = redis.from_url(config.redis_url, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.warning("Redis not available, using memory cache", error=str(e))
    redis_client = None

# Memory caches
status_cache = TTLCache(maxsize=1000, ttl=60)  # 1-minute TTL
metrics_cache = LRUCache(maxsize=500)

# Enhanced SocketIO initialization with better error handling
def initialize_socketio():
    """Initialize SocketIO with fallback modes"""
    socket_configs = [
        {'async_mode': 'gevent', 'logger': False, 'engineio_logger': False},
        {'async_mode': 'eventlet', 'logger': False, 'engineio_logger': False},
        {'async_mode': 'threading', 'logger': False, 'engineio_logger': False}
    ]
    
    for i, socket_config in enumerate(socket_configs):
        try:
            socketio = SocketIO(
                app, 
                cors_allowed_origins="*",
                ping_timeout=60,
                ping_interval=25,
                **socket_config
            )
            logger.info("SocketIO initialized", mode=socket_config['async_mode'])
            return socketio
        except Exception as e:
            logger.warning("SocketIO mode failed", mode=socket_config['async_mode'], error=str(e))
            if i == len(socket_configs) - 1:
                raise RuntimeError("All SocketIO modes failed")

socketio = initialize_socketio()

# Enhanced System Status with comprehensive metrics
@dataclass
class SystemStatus:
    """Comprehensive system status tracking"""
    status: str = 'initializing'
    last_cycle: Optional[datetime] = None
    total_cycles: int = 0
    repositories_managed: int = 0
    last_commit: Optional[str] = None
    agents_active: bool = False
    agents_count: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    uptime: float = 0.0
    errors_count: int = 0
    warnings_count: int = 0
    learning_progress: Dict[str, Any] = None
    blockchain_status: str = 'disabled'
    ai_models_active: List[str] = None
    performance_score: float = 0.0
    security_status: str = 'unknown'
    last_update: datetime = None
    
    def __post_init__(self):
        if self.learning_progress is None:
            self.learning_progress = {}
        if self.ai_models_active is None:
            self.ai_models_active = []
        if self.last_update is None:
            self.last_update = datetime.now()

# Global system state
system_status = SystemStatus()
autonomous_system = None
start_time = datetime.now()
thread_pool = ThreadPoolExecutor(max_workers=4)

# Security utilities
def generate_api_key():
    """Generate secure API key"""
    return Fernet.generate_key().decode()

def verify_api_key(f):
    """Decorator to verify API key for protected endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not config.security_enabled:
            return f(*args, **kwargs)
        
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('XMRT_API_KEY'):
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

# Performance monitoring
def update_system_metrics():
    """Update comprehensive system metrics"""
    try:
        # System metrics
        system_status.memory_usage = psutil.virtual_memory().percent
        system_status.cpu_usage = psutil.cpu_percent(interval=1)
        system_status.uptime = (datetime.now() - start_time).total_seconds()
        
        # Update Prometheus metrics
        AGENT_COUNT.set(system_status.agents_count)
        
        # Calculate health score
        health_factors = {
            'cpu': max(0, 1 - system_status.cpu_usage / 100),
            'memory': max(0, 1 - system_status.memory_usage / 100),
            'agents': 1 if system_status.agents_active else 0,
            'errors': max(0, 1 - system_status.errors_count / 100)
        }
        system_status.performance_score = sum(health_factors.values()) / len(health_factors)
        SYSTEM_HEALTH.set(system_status.performance_score)
        
        system_status.last_update = datetime.now()
        
    except Exception as e:
        logger.error("Failed to update system metrics", error=str(e))
        system_status.errors_count += 1

# Enhanced autonomous system initialization
async def initialize_autonomous_system():
    """Initialize the enhanced autonomous learning system"""
    global autonomous_system, system_status
    
    try:
        logger.info("🤖 Initializing XMRT Enhanced Autonomous Learning System...")
        
        if not config.github_token:
            raise ValueError("GITHUB_TOKEN environment variable not set!")
        
        # Initialize core components with enhanced features
        components = {}
        
        # GitHub Manager with advanced features
        components['github'] = GitHubManager(config.github_token)
        
        # Multi-agent system with coordination
        components['agents'] = MultiAgentSystem(
            max_agents=config.max_agents,
            learning_interval=config.learning_interval
        )
        
        # Memory system with persistent storage
        components['memory'] = MemorySystem(redis_client=redis_client)
        
        # Learning optimizer
        if 'LearningOptimizer' in globals():
            components['optimizer'] = LearningOptimizer()
        
        # Performance analyzer
        if 'PerformanceAnalyzer' in globals():
            components['analyzer'] = PerformanceAnalyzer()
        
        # Web3 integration if enabled
        if config.blockchain_enabled and 'Web3DAppFactory' in globals():
            components['web3'] = Web3DAppFactory()
            system_status.blockchain_status = 'active'
        
        # Analytics system
        if config.analytics_enabled and 'AnalyticsSystem' in globals():
            components['analytics'] = AnalyticsSystem()
        
        # Create enhanced autonomous controller
        autonomous_system = AutonomousController(
            github_token=config.github_token,
            components=components
        )
        
        # Start autonomous learning cycles
        await autonomous_system.start_autonomous_learning()
        
        # Update system status
        system_status.status = 'running'
        system_status.agents_active = True
        system_status.agents_count = len(components.get('agents', {}).get('active_agents', []))
        system_status.ai_models_active = ['GPT-4', 'Claude-3', 'Local-LLM']
        system_status.security_status = 'active' if config.security_enabled else 'disabled'
        
        logger.info("✅ Enhanced autonomous learning system initialized successfully!")
        
        # Start background tasks
        asyncio.create_task(background_health_monitor())
        
    except Exception as e:
        logger.error("❌ Error initializing autonomous system", error=str(e), traceback=traceback.format_exc())
        system_status.status = 'error'
        system_status.errors_count += 1
        raise

async def background_health_monitor():
    """Background task for continuous health monitoring"""
    while True:
        try:
            update_system_metrics()
            
            # Emit real-time updates via WebSocket
            if socketio:
                socketio.emit('system_update', clean_system_status_for_json(asdict(system_status)))
            
            await asyncio.sleep(30)  # Update every 30 seconds
        except Exception as e:
            logger.error("Health monitor error", error=str(e))
            system_status.errors_count += 1
            await asyncio.sleep(60)  # Longer delay on error

# Enhanced Web Interface with modern dashboard
ENHANCED_WEB_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT-Ecosystem Enhanced Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            overflow-x: hidden;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.3);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: #00d4ff;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-running { background-color: #00ff88; }
        .status-error { background-color: #ff4757; }
        .status-initializing { background-color: #ffa502; }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .card-icon {
            font-size: 1.5rem;
            color: #00d4ff;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-value {
            font-weight: bold;
            color: #00ff88;
        }
        
        .chart-container {
            height: 200px;
            margin-top: 1rem;
        }
        
        .log-container {
            max-height: 300px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        
        .log-entry {
            margin-bottom: 0.5rem;
            padding: 0.25rem;
            border-radius: 4px;
        }
        
        .log-info { background: rgba(0, 123, 255, 0.2); }
        .log-warning { background: rgba(255, 193, 7, 0.2); }
        .log-error { background: rgba(220, 53, 69, 0.2); }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #00ff88);
            transition: width 0.3s ease;
        }
        
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .agent-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .agent-card:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .agent-status {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .controls {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 25px;
            background: linear-gradient(45deg, #00d4ff, #00ff88);
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 212, 255, 0.3);
        }
        
        .blockchain-status {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            margin-top: 1rem;
        }
        
        .network-indicator {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: conic-gradient(from 0deg, #00d4ff, #00ff88, #ffa502, #00d4ff);
            animation: rotate 3s linear infinite;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .network-core {
            width: 30px;
            height: 30px;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #00d4ff;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
                padding: 1rem;
            }
            
            .header {
                padding: 1rem;
                flex-direction: column;
                gap: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <i class="fas fa-robot"></i> XMRT-Ecosystem Enhanced
        </div>
        <div class="status-indicator">
            <div class="status-dot status-initializing" id="statusDot"></div>
            <span id="statusText">Initializing...</span>
        </div>
    </div>
    
    <div class="dashboard">
        <!-- System Overview Card -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-tachometer-alt card-icon"></i>
                System Overview
            </div>
            <div class="metric">
                <span>Status:</span>
                <span class="metric-value" id="systemStatus">Initializing</span>
            </div>
            <div class="metric">
                <span>Uptime:</span>
                <span class="metric-value" id="uptime">00:00:00</span>
            </div>
            <div class="metric">
                <span>Total Cycles:</span>
                <span class="metric-value" id="totalCycles">0</span>
            </div>
            <div class="metric">
                <span>Repositories:</span>
                <span class="metric-value" id="repositories">0</span>
            </div>
            <div class="metric">
                <span>Performance Score:</span>
                <span class="metric-value" id="performanceScore">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="performanceBar" style="width: 0%"></div>
            </div>
        </div>
        
        <!-- Agents Status Card -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-users card-icon"></i>
                AI Agents Status
            </div>
            <div class="metric">
                <span>Active Agents:</span>
                <span class="metric-value" id="activeAgents">0</span>
            </div>
            <div class="agent-grid" id="agentGrid">
                <!-- Agent cards will be populated dynamically -->
            </div>
        </div>
        
        <!-- Performance Metrics Card -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-chart-line card-icon"></i>
                Performance Metrics
            </div>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
        </div>
        
        <!-- System Resources Card -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-server card-icon"></i>
                System Resources
            </div>
            <div class="metric">
                <span>CPU Usage:</span>
                <span class="metric-value" id="cpuUsage">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="cpuBar" style="width: 0%"></div>
            </div>
            <div class="metric">
                <span>Memory Usage:</span>
                <span class="metric-value" id="memoryUsage">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="memoryBar" style="width: 0%"></div>
            </div>
        </div>
        
        <!-- Blockchain Integration Card -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-link card-icon"></i>
                Blockchain Integration
            </div>
            <div class="blockchain-status">
                <div class="network-indicator">
                    <div class="network-core">⚡</div>
                </div>
                <div>
                    <div>Status: <span class="metric-value" id="blockchainStatus">Disabled</span></div>
                    <div>Network: <span id="networkName">None</span></div>
                </div>
            </div>
        </div>
        
        <!-- Learning Progress Card -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-brain card-icon"></i>
                Learning Progress
            </div>
            <div class="metric">
                <span>Learning Cycles:</span>
                <span class="metric-value" id="learningCycles">0</span>
            </div>
            <div class="metric">
                <span>Improvements Made:</span>
                <span class="metric-value" id="improvements">0</span>
            </div>
            <div class="metric">
                <span>Success Rate:</span>
                <span class="metric-value" id="successRate">0%</span>
            </div>
        </div>
        
        <!-- System Logs Card -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-file-alt card-icon"></i>
                System Logs
            </div>
            <div class="log-container" id="logContainer">
                <div class="log-entry log-info">[INFO] System initializing...</div>
            </div>
            <div class="controls">
                <button class="btn" onclick="clearLogs()"><i class="fas fa-trash"></i> Clear</button>
                <button class="btn" onclick="downloadLogs()"><i class="fas fa-download"></i> Export</button>
            </div>
        </div>
        
        <!-- AI Models Card -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-robot card-icon"></i>
                AI Models
            </div>
            <div id="aiModels">
                <div class="metric">
                    <span>Available Models:</span>
                    <span class="metric-value" id="modelCount">0</span>
                </div>
                <div id="modelList"></div>
            </div>
        </div>
    </div>

    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        // Chart.js setup for performance monitoring
        const ctx = document.getElementById('performanceChart').getContext('2d');
        const performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Performance Score',
                    data: [],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    tension: 0.4
                }, {
                    label: 'CPU Usage',
                    data: [],
                    borderColor: '#ffa502',
                    backgroundColor: 'rgba(255, 165, 2, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    x: { 
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: { 
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
        
        // Update dashboard with system data
        function updateDashboard(data) {
            // Update status indicator
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            statusDot.className = `status-dot status-${data.status}`;
            statusText.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
            
            // Update system overview
            document.getElementById('systemStatus').textContent = data.status;
            document.getElementById('uptime').textContent = formatUptime(data.uptime || 0);
            document.getElementById('totalCycles').textContent = data.total_cycles || 0;
            document.getElementById('repositories').textContent = data.repositories_managed || 0;
            
            const perfScore = Math.round((data.performance_score || 0) * 100);
            document.getElementById('performanceScore').textContent = `${perfScore}%`;
            document.getElementById('performanceBar').style.width = `${perfScore}%`;
            
            // Update agents
            document.getElementById('activeAgents').textContent = data.agents_count || 0;
            updateAgentGrid(data.ai_models_active || []);
            
            // Update resources
            const cpuUsage = Math.round(data.cpu_usage || 0);
            const memoryUsage = Math.round(data.memory_usage || 0);
            
            document.getElementById('cpuUsage').textContent = `${cpuUsage}%`;
            document.getElementById('cpuBar').style.width = `${cpuUsage}%`;
            document.getElementById('memoryUsage').textContent = `${memoryUsage}%`;
            document.getElementById('memoryBar').style.width = `${memoryUsage}%`;
            
            // Update blockchain status
            document.getElementById('blockchainStatus').textContent = data.blockchain_status || 'Disabled';
            
            // Update learning progress
            const learningProgress = data.learning_progress || {};
            document.getElementById('learningCycles').textContent = learningProgress.cycles || 0;
            document.getElementById('improvements').textContent = learningProgress.improvements || 0;
            document.getElementById('successRate').textContent = `${learningProgress.success_rate || 0}%`;
            
            // Update AI models
            updateAIModels(data.ai_models_active || []);
            
            // Update performance chart
            updatePerformanceChart(perfScore, cpuUsage);
            
            // Add log entry
            addLogEntry('info', `System update received - Status: ${data.status}`);
        }
        
        function updateAgentGrid(agents) {
            const agentGrid = document.getElementById('agentGrid');
            agentGrid.innerHTML = '';
            
            agents.forEach((agent, index) => {
                const agentCard = document.createElement('div');
                agentCard.className = 'agent-card';
                agentCard.innerHTML = `
                    <div class="agent-status">🤖</div>
                    <div>${agent}</div>
                `;
                agentGrid.appendChild(agentCard);
            });
        }
        
        function updateAIModels(models) {
            const modelCount = document.getElementById('modelCount');
            const modelList = document.getElementById('modelList');
            
            modelCount.textContent = models.length;
            
            modelList.innerHTML = '';
            models.forEach(model => {
                const modelDiv = document.createElement('div');
                modelDiv.className = 'metric';
                modelDiv.innerHTML = `
                    <span>${model}:</span>
                    <span class="metric-value">Active</span>
                `;
                modelList.appendChild(modelDiv);
            });
        }
        
        function updatePerformanceChart(performance, cpu) {
            const now = new Date().toLocaleTimeString();
            const chart = performanceChart;
            
            // Keep only last 20 data points
            if (chart.data.labels.length >= 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
                chart.data.datasets[1].data.shift();
            }
            
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(performance);
            chart.data.datasets[1].data.push(cpu);
            
            chart.update('none');
        }
        
        function addLogEntry(level, message) {
            const logContainer = document.getElementById('logContainer');
            const timestamp = new Date().toLocaleTimeString();
            
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry log-${level}`;
            logEntry.textContent = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
            
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // Keep only last 50 log entries
            while (logContainer.children.length > 50) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }
        
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        
        function clearLogs() {
            document.getElementById('logContainer').innerHTML = '';
            addLogEntry('info', 'Logs cleared');
        }
        
        function downloadLogs() {
            const logs = document.getElementById('logContainer').innerText;
            const blob = new Blob([logs], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `xmrt-logs-${new Date().toISOString().split('T')[0]}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        // Socket.IO event handlers
        socket.on('connect', function() {
            addLogEntry('info', 'Connected to XMRT Dashboard');
            socket.emit('request_status');
        });
        
        socket.on('disconnect', function() {
            addLogEntry('warning', 'Disconnected from XMRT Dashboard');
        });
        
        socket.on('system_update', function(data) {
            updateDashboard(data);
        });
        
        socket.on('log_message', function(data) {
            addLogEntry(data.level, data.message);
        });
        
        // Request status updates every 30 seconds
        setInterval(() => {
            socket.emit('request_status');
        }, 30000);
        
        // Initialize dashboard
        addLogEntry('info', 'XMRT Enhanced Dashboard initialized');
    </script>
</body>
</html>
"""

# Enhanced API Routes
@app.before_request
def before_request():
    """Enhanced request preprocessing"""
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    request.start_time = time.time()

@app.after_request
def after_request(response):
    """Enhanced response postprocessing"""
    request_latency = time.time() - request.start_time
    REQUEST_LATENCY.observe(request_latency)
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

@app.route('/')
def index():
    """Enhanced main dashboard"""
    return render_template_string(ENHANCED_WEB_INTERFACE)

@app.route('/status')
@verify_api_key
def status():
    """Enhanced API endpoint for system status"""
    try:
        update_system_metrics()
        status_data = asdict(system_status)
        
        # Cache the status
        if redis_client:
            redis_client.setex('system_status', 60, json.dumps(status_data, cls=EnhancedJSONEncoder))
        
        return jsonify(status_data)
    except Exception as e:
        logger.error("Status endpoint error", error=str(e))
        return jsonify({'error': 'Status unavailable'}), 500

@app.route('/health')
def health():
    """Enhanced health check endpoint"""
    health_data = {
        'status': 'healthy' if system_status.status != 'error' else 'unhealthy',
        'autonomous_system': autonomous_system is not None,
        'timestamp': datetime.now().isoformat(),
        'uptime': (datetime.now() - start_time).total_seconds(),
        'version': '2.0-enhanced',
        'components': {
            'redis': redis_client is not None,
            'socketio': socketio is not None,
            'blockchain': system_status.blockchain_status == 'active',
            'agents': system_status.agents_active
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return make_response(generate_latest(), 200, {'Content-Type': 'text/plain'})

@app.route('/api/agents')
@verify_api_key
def get_agents():
    """Get active agents information"""
    if autonomous_system:
        agents_info = autonomous_system.get_agents_status()
        return jsonify(agents_info)
    return jsonify({'agents': []})

@app.route('/api/learning/progress')
@verify_api_key
def get_learning_progress():
    """Get detailed learning progress"""
    if autonomous_system:
        progress = autonomous_system.get_learning_progress()
        return jsonify(progress)
    return jsonify({'progress': {}})

@app.route('/api/repositories')
@verify_api_key
def get_repositories():
    """Get managed repositories information"""
    if autonomous_system:
        repos = autonomous_system.get_managed_repositories()
        return jsonify(repos)
    return jsonify({'repositories': []})

@app.route('/api/system/optimize', methods=['POST'])
@verify_api_key
def optimize_system():
    """Trigger system optimization"""
    try:
        if autonomous_system:
            result = autonomous_system.optimize_performance()
            return jsonify({'success': True, 'result': result})
        return jsonify({'success': False, 'error': 'System not initialized'})
    except Exception as e:
        logger.error("Optimization error", error=str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# Enhanced WebSocket event handlers
def clean_system_status_for_json(status):
    """Enhanced JSON serialization with better error handling"""
    try:
        return json.loads(json.dumps(status, cls=EnhancedJSONEncoder))
    except Exception as e:
        logger.error("JSON serialization error", error=str(e))
        return {'error': 'Serialization failed'}

@socketio.on('connect')
def handle_connect():
    """Enhanced WebSocket connection handler"""
    try:
        client_info = {
            'ip': request.environ.get('REMOTE_ADDR'),
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Client connected to dashboard", client_info=client_info)
        
        # Send initial system status
        emit('system_update', clean_system_status_for_json(asdict(system_status)))
        
        # Join monitoring room for broadcasts
        join_room('monitors')
        
    except Exception as e:
        logger.error("WebSocket connection error", error=str(e))

@socketio.on('disconnect')
def handle_disconnect():
    """Enhanced WebSocket disconnection handler"""
    try:
        leave_room('monitors')
        logger.info("Client disconnected from dashboard")
    except Exception as e:
        logger.error("WebSocket disconnection error", error=str(e))

@socketio.on('request_status')
def handle_status_request():
    """Enhanced status request handler"""
    try:
        update_system_metrics()
        emit('system_update', clean_system_status_for_json(asdict(system_status)))
    except Exception as e:
        logger.error("Status request error", error=str(e))
        emit('error', {'message': 'Status unavailable'})

@socketio.on('request_logs')
def handle_logs_request():
    """Handle logs request"""
    try:
        # Send recent logs (this would be implemented with proper log storage)
        emit('logs_update', {'logs': []})
    except Exception as e:
        logger.error("Logs request error", error=str(e))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error("Internal server error", error=str(error))
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error("Unhandled exception", error=str(e), traceback=traceback.format_exc())
    system_status.errors_count += 1
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Enhanced startup
async def startup_system():
    """Enhanced system startup sequence"""
    try:
        logger.info("🚀 Starting XMRT-Ecosystem Enhanced v2.0")
        
        # Initialize autonomous system
        await initialize_autonomous_system()
        
        # Start health monitoring
        logger.info("✅ System startup completed successfully")
        
    except Exception as e:
        logger.error("❌ System startup failed", error=str(e))
        system_status.status = 'error'
        raise

if __name__ == '__main__':
    try:
        # Initialize system in background
        if config.debug_mode:
            # For development, run synchronously
            asyncio.run(startup_system())
        else:
            # For production, run in background thread
            init_thread = threading.Thread(
                target=lambda: asyncio.run(startup_system()), 
                daemon=True
            )
            init_thread.start()
        
        # Get port from environment
        port = int(os.environ.get('PORT', 5000))
        
        logger.info(
            "🚀 Starting XMRT-Ecosystem Enhanced Dashboard", 
            port=port, 
            debug=config.debug_mode,
            config=asdict(config)
        )
        
        # Run the enhanced Flask-SocketIO app
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=port, 
            debug=config.debug_mode,
            use_reloader=False,  # Disable reloader to prevent issues
            log_output=not config.debug_mode
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down XMRT-Ecosystem Enhanced")
        sys.exit(0)
    except Exception as e:
        logger.error("❌ Failed to start application", error=str(e))
        sys.exit(1)