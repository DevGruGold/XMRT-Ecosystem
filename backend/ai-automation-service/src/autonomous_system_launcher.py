#!/usr/bin/env python3
"""
Autonomous System Launcher
Launches and manages the unified autonomous system with proper error handling
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import with error handling
try:
    from unified_autonomous_system import (
        UnifiedAutonomousSystem,
        SystemIntegrationConfig,
        DecisionLevel,
        UnifiedSystemState,
    )

    UNIFIED_SYSTEM_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import unified_autonomous_system: {e}")
    UNIFIED_SYSTEM_AVAILABLE = False

    # Define fallback classes
    class DecisionLevel(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    @dataclass
    class SystemIntegrationConfig:
        github_token: str
        openai_api_key: str
        monitoring_endpoint: str
        orchestration_mode: str = "autonomous"
        decision_thresholds: Optional[Dict[DecisionLevel, float]] = None

        def __post_init__(self):
            if self.decision_thresholds is None:
                self.decision_thresholds = {
                    DecisionLevel.LOW: 0.3,
                    DecisionLevel.MEDIUM: 0.5,
                    DecisionLevel.HIGH: 0.7,
                    DecisionLevel.CRITICAL: 0.9,
                }

    class UnifiedSystemState(Enum):
        INITIALIZING = "initializing"
        RUNNING = "running"
        STOPPED = "stopped"
        ERROR = "error"

    class UnifiedAutonomousSystem:
        def __init__(self, config):
            self.config = config
            self.state = UnifiedSystemState.ERROR
            self.logger = logging.getLogger("UnifiedAutonomousSystem")
            self.logger.error(
                "UnifiedAutonomousSystem not available due to import errors"
            )

        async def initialize(self):
            self.logger.error("Cannot initialize - system not available")
            return False

        async def start(self):
            self.logger.error("Cannot start - system not available")
            return False

        async def stop(self):
            self.logger.info("Stopping placeholder system")
            return True


class AutonomousSystemLauncher:
    """Launcher for the autonomous system with comprehensive error handling"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.system: Optional[UnifiedAutonomousSystem] = None
        self.config: Optional[SystemIntegrationConfig] = None

    def _setup_logger(self):
        """Setup logging configuration"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def load_config(self) -> SystemIntegrationConfig:
        """Load configuration from environment variables"""
        self.logger.info("Loading configuration from environment...")

        github_token = os.getenv("GITHUB_TOKEN", "")
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        monitoring_endpoint = os.getenv(
            "MONITORING_ENDPOINT", "http://localhost:9090/metrics"
        )
        orchestration_mode = os.getenv("ORCHESTRATION_MODE", "autonomous")

        if not github_token:
            self.logger.warning("GITHUB_TOKEN not set in environment")
        if not openai_api_key:
            self.logger.warning("OPENAI_API_KEY not set in environment")

        config = SystemIntegrationConfig(
            github_token=github_token,
            openai_api_key=openai_api_key,
            monitoring_endpoint=monitoring_endpoint,
            orchestration_mode=orchestration_mode,
        )

        self.logger.info(f"Configuration loaded: mode={config.orchestration_mode}")
        return config

    async def initialize_system(self) -> bool:
        """Initialize the autonomous system"""
        try:
            self.config = self.load_config()

            if not UNIFIED_SYSTEM_AVAILABLE:
                self.logger.error(
                    "UnifiedAutonomousSystem not available - cannot initialize"
                )
                return False

            self.logger.info("Initializing UnifiedAutonomousSystem...")
            self.system = UnifiedAutonomousSystem(self.config)

            await self.system.initialize()
            self.logger.info("System initialization completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            return False

    async def start_system(self) -> bool:
        """Start the autonomous system"""
        if not self.system:
            self.logger.error("System not initialized - cannot start")
            return False

        try:
            self.logger.info("Starting autonomous system...")
            await self.system.start()
            return True

        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            return False

    async def stop_system(self) -> bool:
        """Stop the autonomous system"""
        if not self.system:
            self.logger.warning("No system to stop")
            return True

        try:
            self.logger.info("Stopping autonomous system...")
            await self.system.stop()
            self.logger.info("System stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop system: {e}")
            return False

    async def run(self):
        """Main run loop"""
        self.logger.info("Starting Autonomous System Launcher...")

        # Initialize system
        if not await self.initialize_system():
            self.logger.error("System initialization failed - exiting")
            return False

        # Start system
        try:
            await self.start_system()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal - shutting down...")
        except Exception as e:
            self.logger.error(f"Unexpected error during system operation: {e}")
        finally:
            await self.stop_system()

        self.logger.info("Autonomous System Launcher finished")
        return True


async def main():
    """Main entry point"""
    launcher = AutonomousSystemLauncher()

    try:
        await launcher.run()
    except Exception as e:
        logging.error(f"Fatal error in launcher: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Launcher interrupted by user")
    except Exception as e:
        logging.error(f"Launcher failed with error: {e}")
        sys.exit(1)
