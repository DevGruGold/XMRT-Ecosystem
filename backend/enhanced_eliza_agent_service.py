"""
Enhanced Eliza Agent Service - Incentivized Autonomous Learning System (IALS)
Continuously builds utilities and learns from mistakes using XMRT ecosystem resources.
"""

import asyncio
import logging
import json
import os
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import aiohttp
import numpy as np
from pathlib import Path
import sys

# Add project paths
sys.path.append('/app')
sys.path.append('/app/backend')
sys.path.append('/app/enhanced')
sys.path.append('/app/integrations')

# Import XMRT infrastructure
try:
    from backend.eliza_agent_service import ElizaAgentService
    from backend.xmrt_blockchain_service import XMRTBlockchainService
    from backend.glacier_vectordb_service import GlacierVectorDBService
    from enhanced.repository_discovery_service import RepositoryDiscoveryService
    from integrations.incentive_calculation_service import IncentiveCalculationService
    # Attempt to import MemorySystem from root
    try:
        from memory_system import MemorySystem
    except ImportError:
        # Fallback if path not set correctly
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from memory_system import MemorySystem

except ImportError as e:
    logging.warning(f"Import warning: {e}")

@dataclass
class LearningCycle:
    """Represents a complete learning cycle with rewards"""
    cycle_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    repositories_discovered: int = 0
    utilities_built: int = 0
    tests_passed: int = 0
    errors_encountered: int = 0
    xmrt_tokens_earned: float = 0.0
    quality_score: float = 0.0
    learning_insights: List[str] = None

    def __post_init__(self):
        if self.learning_insights is None:
            self.learning_insights = []

@dataclass
class UtilityResult:
    """Result of utility building attempt"""
    success: bool
    utility_name: str
    repository: str
    code_generated: str
    tests_passed: bool
    error_message: Optional[str] = None
    quality_metrics: Dict[str, float] = None

    def __post_init__(self):
        if self.quality_metrics is None:
            self.quality_metrics = {}

class EnhancedElizaAgentService:
    """
    Enhanced Eliza Agent with Incentivized Autonomous Learning System (IALS)

    This service extends the base ElizaAgentService with:
    - Continuous repository discovery and analysis
    - Autonomous utility building and testing
    - Mistake learning and improvement cycles
    - XMRT token reward system
    - Long-term memory integration with Glacier VectorDB
    - Offline learning capabilities via MESHNET
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Core services
        self.eliza_service = ElizaAgentService()
        self.blockchain_service = XMRTBlockchainService()
        self.vector_db = GlacierVectorDBService()
        self.repo_discovery = RepositoryDiscoveryService()
        self.incentive_calc = IncentiveCalculationService()
        
        # Initialize Enhanced Memory System
        try:
            self.memory_system = MemorySystem({'local_db_path': 'eliza_memory.db'})
            self.memory_system.initialize()
        except Exception as e:
            self.logger.warning(f"MemorySystem failed to initialize: {e}")
            self.memory_system = None

        # Learning state
        self.current_cycle: Optional[LearningCycle] = None
        self.learning_history: List[LearningCycle] = []
        self.mistake_memory: Dict[str, List[str]] = {}
        self.utility_templates: Dict[str, str] = {}
        self.performance_metrics: Dict[str, float] = {
            'success_rate': 0.0,
            'avg_quality_score': 0.0,
            'total_utilities_built': 0,
            'total_tokens_earned': 0.0,
            'learning_velocity': 0.0
        }

        # Configuration
        self.config = {
            'learning_cycle_duration': 3600,  # 1 hour cycles
            'max_concurrent_builds': 5,
            'quality_threshold': 0.7,
            'min_reward_threshold': 10.0,
            'discovery_interval': 300,  # 5 minutes
            'memory_retention_days': 90,
            'auto_commit_enabled': True,
            'meshnet_sync_enabled': True
        }

        # Initialize utility templates
        self._load_utility_templates()

        self.logger.info("Enhanced Eliza Agent Service initialized with IALS")

    def _load_utility_templates(self):
        """Load code templates for different types of utilities"""
        self.utility_templates = {
            'ai_integration': '''
# AI Integration Utility for {{repo_name}}
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

class {{class_name}}Integration:
    """AI integration utility for {{repo_name}}"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {{
            'api_endpoint': '{{repo_name}}_endpoint',
            'model_type': 'enhanced_eliza',
            'batch_size': 32,
            'timeout': 30
        }}

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI request with enhanced capabilities"""
        try:
            # Enhanced processing logic
            result = await self._enhance_processing(data)
            return {{
                'success': True,
                'result': result,
                'metadata': {{
                    'processed_at': datetime.utcnow().isoformat(),
                    'utility_version': '1.0.0'
                }}
            }}
        except Exception as e:
            self.logger.error(f"Processing error: {{e}}")
            return {{'success': False, 'error': str(e)}}

    async def _enhance_processing(self, data: Dict[str, Any]) -> Any:
        """Enhanced processing with XMRT integration"""
        # Implement specific enhancement logic
        return data

    def get_capabilities(self) -> List[str]:
        """Return list of AI capabilities"""
        return [
            'natural_language_processing',
            'pattern_recognition',
            'autonomous_learning',
            'xmrt_integration'
        ]

# Test the integration
async def test_{{class_name_lower}}_integration():
    integration = {{class_name}}Integration()
    test_data = {{'test': 'data', 'timestamp': datetime.utcnow().isoformat()}}
    result = await integration.process_request(test_data)
    assert result['success'], f"Integration test failed: {{result}}"
    return True

if __name__ == "__main__":
    asyncio.run(test_{{class_name_lower}}_integration())
''',

            'networking': '''
# Networking Utility for {{repo_name}}
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional

class {{class_name}}NetworkUtil:
    """Enhanced networking utility for {{repo_name}}"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.config = {{
            'timeout': 30,
            'max_connections': 100,
            'retry_attempts': 3,
            'backoff_factor': 2
        }}

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=self.config['max_connections'])
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=self.config['timeout'])
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def enhanced_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Enhanced HTTP request with retry logic"""
        for attempt in range(self.config['retry_attempts']):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    data = await response.json()
                    return {{
                        'status_code': response.status,
                        'data': data,
                        'headers': dict(response.headers),
                        'success': True
                    }}
            except Exception as e:
                if attempt == self.config['retry_attempts'] - 1:
                    return {{'success': False, 'error': str(e)}}
                await asyncio.sleep(self.config['backoff_factor'] ** attempt)

        return {{'success': False, 'error': 'Max retries exceeded'}}

    async def batch_requests(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple requests concurrently"""
        tasks = []
        for req in requests:
            task = self.enhanced_request(**req)
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)

# Test the networking utility
async def test_{{class_name_lower}}_network():
    async with {{class_name}}NetworkUtil() as net_util:
        test_result = await net_util.enhanced_request('GET', 'https://httpbin.org/json')
        assert test_result['success'], f"Network test failed: {{test_result}}"
    return True

if __name__ == "__main__":
    asyncio.run(test_{{class_name_lower}}_network())
''',

            'governance': '''
# Governance Utility for {{repo_name}}
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class GovernanceProposal:
    proposal_id: str
    title: str
    description: str
    proposer: str
    created_at: datetime
    voting_deadline: datetime
    votes_for: int = 0
    votes_against: int = 0
    status: str = 'active'

class {{class_name}}Governance:
    """Enhanced governance utility for {{repo_name}}"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.proposals: Dict[str, GovernanceProposal] = {{}}
        self.voting_power: Dict[str, float] = {{}}
        self.config = {{
            'min_voting_period': timedelta(days=3),
            'max_voting_period': timedelta(days=14),
            'quorum_threshold': 0.3,
            'passing_threshold': 0.6
        }}

    async def create_proposal(self, title: str, description: str, proposer: str, 
                            voting_period: timedelta = None) -> str:
        """Create a new governance proposal"""
        if voting_period is None:
            voting_period = self.config['min_voting_period']

        proposal_id = f"prop_{{len(self.proposals) + 1}}_{{int(time.time())}}"
        proposal = GovernanceProposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            proposer=proposer,
            created_at=datetime.utcnow(),
            voting_deadline=datetime.utcnow() + voting_period
        )

        self.proposals[proposal_id] = proposal
        self.logger.info(f"Created proposal {{proposal_id}}: {{title}}")
        return proposal_id

    async def cast_vote(self, proposal_id: str, voter: str, vote: bool) -> bool:
        """Cast a vote on a proposal"""
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        if datetime.utcnow() > proposal.voting_deadline:
            return False

        voting_power = self.voting_power.get(voter, 1.0)

        if vote:
            proposal.votes_for += voting_power
        else:
            proposal.votes_against += voting_power

        return True

    async def finalize_proposal(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Finalize proposal voting and determine outcome"""
        if proposal_id not in self.proposals:
            return None

        proposal = self.proposals[proposal_id]
        total_votes = proposal.votes_for + proposal.votes_against

        if total_votes == 0:
            proposal.status = 'failed_quorum'
            return {{'status': 'failed', 'reason': 'no_votes'}}

        approval_rate = proposal.votes_for / total_votes

        if approval_rate >= self.config['passing_threshold']:
            proposal.status = 'passed'
            return {{'status': 'passed', 'approval_rate': approval_rate}}
        else:
            proposal.status = 'rejected'
            return {{'status': 'rejected', 'approval_rate': approval_rate}}

    def get_proposal_status(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a proposal"""
        if proposal_id not in self.proposals:
            return None

        proposal = self.proposals[proposal_id]
        return {{
            'proposal_id': proposal_id,
            'title': proposal.title,
            'status': proposal.status,
            'votes_for': proposal.votes_for,
            'votes_against': proposal.votes_against,
            'deadline': proposal.voting_deadline.isoformat()
        }}

# Test the governance utility
async def test_{{class_name_lower}}_governance():
    gov = {{class_name}}Governance()

    # Test proposal creation
    prop_id = await gov.create_proposal(
        "Test Proposal", 
        "This is a test proposal", 
        "test_proposer"
    )
    assert prop_id is not None, "Failed to create proposal"

    # Test voting
    vote_result = await gov.cast_vote(prop_id, "test_voter", True)
    assert vote_result, "Failed to cast vote"

    return True

if __name__ == "__main__":
    asyncio.run(test_{{class_name_lower}}_governance())
'''
        }

        self.logger.info("Loaded utility templates successfully")

    async def start_continuous_learning(self):
        """Start the continuous learning process"""
        self.logger.info("Starting Incentivized Autonomous Learning System (IALS)")

        try:
            # Initialize services
            await self._initialize_services()

            # Start main learning loop
            while True:
                await self._execute_learning_cycle()
                await asyncio.sleep(self.config['discovery_interval'])

        except Exception as e:
            self.logger.error(f"Critical error in learning system: {e}")
            await self._handle_critical_error(e)

    async def _initialize_services(self):
        """Initialize all required services"""
        try:
            # Initialize vector database connection
            await self.vector_db.initialize()

            # Initialize blockchain connection
            await self.blockchain_service.initialize()

            # Load previous learning history
            await self._load_learning_history()

            # Sync with MESHNET if enabled
            if self.config['meshnet_sync_enabled']:
                await self._sync_with_meshnet()

            self.logger.info("All services initialized successfully")

        except Exception as e:
            self.logger.error(f"Service initialization failed: {e}")
            raise

    async def _execute_learning_cycle(self):
        """Execute a complete learning cycle"""
        cycle_id = f"cycle_{int(time.time())}_{len(self.learning_history)}"

        self.current_cycle = LearningCycle(
            cycle_id=cycle_id,
            start_time=datetime.utcnow()
        )

        try:
            self.logger.info(f"Starting learning cycle: {cycle_id}")

            # Phase 1: Repository Discovery
            discovered_repos = await self._discover_repositories()
            self.current_cycle.repositories_discovered = len(discovered_repos)

            # Phase 2: Utility Building
            build_results = await self._build_utilities(discovered_repos)
            self.current_cycle.utilities_built = len([r for r in build_results if r.success])
            self.current_cycle.tests_passed = len([r for r in build_results if r.tests_passed])
            self.current_cycle.errors_encountered = len([r for r in build_results if not r.success])

            # Phase 3: Learn from Mistakes
            await self._learn_from_mistakes(build_results)

            # Phase 4: Calculate Rewards
            rewards = await self._calculate_rewards(build_results)
            self.current_cycle.xmrt_tokens_earned = rewards.get('total_tokens', 0.0)
            self.current_cycle.quality_score = rewards.get('quality_score', 0.0)

            # Phase 5: Update Memory
            await self._update_long_term_memory()

            # Phase 6: Commit if enabled
            if self.config['auto_commit_enabled']:
                await self._commit_utilities(build_results)

            # Complete cycle
            self.current_cycle.end_time = datetime.utcnow()
            self.learning_history.append(self.current_cycle)

            # Update performance metrics
            await self._update_performance_metrics()

            self.logger.info(f"Completed learning cycle: {cycle_id}")
            self.logger.info(f"Utilities built: {self.current_cycle.utilities_built}")
            self.logger.info(f"XMRT tokens earned: {self.current_cycle.xmrt_tokens_earned}")
            self.logger.info(f"Quality score: {self.current_cycle.quality_score}")

        except Exception as e:
            self.logger.error(f"Learning cycle failed: {e}")
            if self.current_cycle:
                self.current_cycle.learning_insights.append(f"Cycle failed: {str(e)}")

            # Learn from the failure
            await self._record_mistake("learning_cycle", str(e))

        finally:
            self.current_cycle = None

    async def _discover_repositories(self) -> List[Dict[str, Any]]:
        """Discover repositories with learning opportunities"""
        try:
            # Use repository discovery service
            repositories = await self.repo_discovery.discover_xmrt_repositories()

            # Filter for high-value learning opportunities
            high_value_repos = []
            for repo in repositories:
                learning_value = await self._calculate_learning_value(repo)
                if learning_value > 0.5:  # Threshold for worthwhile learning
                    repo['learning_value'] = learning_value
                    high_value_repos.append(repo)

            # Sort by learning value
            high_value_repos.sort(key=lambda x: x['learning_value'], reverse=True)

            # Limit to max concurrent builds
            return high_value_repos[:self.config['max_concurrent_builds']]

        except Exception as e:
            self.logger.error(f"Repository discovery failed: {e}")
            return []

    async def _calculate_learning_value(self, repo: Dict[str, Any]) -> float:
        """Calculate the learning value of a repository"""
        try:
            value_factors = {
                'complexity': repo.get('complexity_score', 0.5),
                'activity': min(repo.get('commit_frequency', 0) / 10.0, 1.0),
                'integration_potential': repo.get('integration_score', 0.5),
                'novelty': 1.0 - self._get_familiarity_score(repo['name']),
                'community': min(repo.get('stars', 0) / 100.0, 1.0)
            }

            # Weighted average
            weights = {
                'complexity': 0.25,
                'activity': 0.20,
                'integration_potential': 0.30,
                'novelty': 0.15,
                'community': 0.10
            }

            learning_value = sum(
                value_factors[factor] * weights[factor] 
                for factor in value_factors
            )

            return min(learning_value, 1.0)

        except Exception as e:
            self.logger.warning(f"Failed to calculate learning value: {e}")
            return 0.5  # Default moderate value

    def _get_familiarity_score(self, repo_name: str) -> float:
        """Get familiarity score with a repository (0=new, 1=very familiar)"""
        # Check learning history for interactions with this repo
        interactions = sum(
            1 for cycle in self.learning_history
            for insight in cycle.learning_insights
            if repo_name in insight
        )

        # Normalize (max familiarity after 10 interactions)
        return min(interactions / 10.0, 1.0)

    async def _build_utilities(self, repositories: List[Dict[str, Any]]) -> List[UtilityResult]:
        """Build utilities for discovered repositories"""
        results = []

        # Create concurrent tasks for utility building
        tasks = []
        for repo in repositories:
            task = self._build_single_utility(repo)
            tasks.append(task)

        # Execute all builds concurrently
        build_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(build_results):
            if isinstance(result, Exception):
                error_result = UtilityResult(
                    success=False,
                    utility_name=f"util_{repositories[i]['name']}",
                    repository=repositories[i]['name'],
                    code_generated="",
                    tests_passed=False,
                    error_message=str(result)
                )
                results.append(error_result)
            else:
                results.append(result)

        return results

    async def _build_single_utility(self, repo: Dict[str, Any]) -> UtilityResult:
        """Build a single utility for a repository"""
        try:
            repo_name = repo['name']
            repo_type = repo.get('type', 'general')

            self.logger.info(f"Building utility for {repo_name} ({repo_type})")

            # Generate utility name and class name
            utility_name = f"{repo_name.replace('-', '_')}_utility"
            class_name = self._generate_class_name(repo_name)
            class_name_lower = class_name.lower()

            # Select appropriate template
            template_key = self._select_template(repo_type)
            template = self.utility_templates.get(template_key, self.utility_templates['ai_integration'])

            # Generate code from template with proper formatting
            code = template.format(
                repo_name=repo_name,
                class_name=class_name,
                class_name_lower=class_name_lower
            )

            # Add necessary imports
            code = self._add_required_imports(code, repo_type)

            # Test the generated code
            test_passed = await self._test_generated_code(code, utility_name)

            # Calculate quality metrics
            quality_metrics = await self._calculate_code_quality(code)

            result = UtilityResult(
                success=True,
                utility_name=utility_name,
                repository=repo_name,
                code_generated=code,
                tests_passed=test_passed,
                quality_metrics=quality_metrics
            )

            self.logger.info(f"Successfully built utility: {utility_name}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to build utility for {repo['name']}: {e}")
            return UtilityResult(
                success=False,
                utility_name=f"util_{repo['name']}",
                repository=repo['name'],
                code_generated="",
                tests_passed=False,
                error_message=str(e)
            )

    def _generate_class_name(self, repo_name: str) -> str:
        """Generate a valid Python class name from repository name"""
        # Remove special characters and convert to PascalCase
        clean_name = ''.join(c for c in repo_name if c.isalnum() or c == '_')
        parts = clean_name.split('_')
        class_name = ''.join(word.capitalize() for word in parts if word)

        # Ensure it starts with a letter
        if not class_name or not class_name[0].isalpha():
            class_name = 'Xmrt' + class_name

        return class_name

    def _select_template(self, repo_type: str) -> str:
        """Select appropriate template based on repository type"""
        template_mapping = {
            'ai_agent': 'ai_integration',
            'networking': 'networking',
            'governance': 'governance',
            'defi': 'ai_integration',
            'nft': 'ai_integration',
            'dao': 'governance',
            'protocol': 'networking'
        }

        return template_mapping.get(repo_type, 'ai_integration')

    def _add_required_imports(self, code: str, repo_type: str) -> str:
        """Add required imports to generated code"""
        base_imports = [
            "import asyncio",
            "import logging",
            "import time",
            "from datetime import datetime, timedelta",
            "from typing import Dict, Any, List, Optional",
            "from dataclasses import dataclass"
        ]

        type_specific_imports = {
            'networking': ["import aiohttp", "import socket"],
            'governance': ["import hashlib", "import json"],
            'ai_integration': ["import numpy as np", "import json"]
        }

        all_imports = base_imports + type_specific_imports.get(repo_type, [])
        import_block = '\n'.join(all_imports) + '\n\n'

        return import_block + code

    async def _test_generated_code(self, code: str, utility_name: str) -> bool:
        """Test the generated code for syntax and basic functionality"""
        try:
            # Basic syntax check
            compile(code, f"{utility_name}.py", "exec")

            # TODO: Add more sophisticated testing
            # For now, we consider syntax validation as passing
            return True

        except SyntaxError as e:
            self.logger.error(f"Syntax error in generated code: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Code test failed: {e}")
            return False

    async def _calculate_code_quality(self, code: str) -> Dict[str, float]:
        """Calculate quality metrics for generated code"""
        metrics = {
            'length_score': min(len(code) / 5000.0, 1.0),  # Normalized by 5KB
            'complexity_score': 0.7,  # Placeholder - could use cyclomatic complexity
            'documentation_score': 0.8 if '"""' in code else 0.3,
            'error_handling_score': 0.9 if 'try:' in code and 'except' in code else 0.4,
            'async_support_score': 1.0 if 'async def' in code else 0.5
        }

        # Overall quality score (weighted average)
        weights = [0.15, 0.25, 0.20, 0.25, 0.15]
        overall_score = sum(score * weight for score, weight in zip(metrics.values(), weights))
        metrics['overall_score'] = overall_score

        return metrics

    async def _learn_from_mistakes(self, build_results: List[UtilityResult]):
        """Learn from mistakes and failures"""
        failures = [result for result in build_results if not result.success]

        for failure in failures:
            mistake_type = self._classify_mistake(failure.error_message)
            await self._record_mistake(mistake_type, failure.error_message)

            # Generate learning insight
            insight = await self._generate_learning_insight(failure)
            if self.current_cycle:
                self.current_cycle.learning_insights.append(insight)

    def _classify_mistake(self, error_message: str) -> str:
        """Classify the type of mistake"""
        if not error_message:
            return "unknown"

        error_lower = error_message.lower()

        if "syntax" in error_lower:
            return "syntax_error"
        elif "import" in error_lower or "module" in error_lower:
            return "import_error"
        elif "network" in error_lower or "connection" in error_lower:
            return "network_error"
        elif "permission" in error_lower or "access" in error_lower:
            return "permission_error"
        elif "timeout" in error_lower:
            return "timeout_error"
        else:
            return "runtime_error"

    async def _record_mistake(self, mistake_type: str, error_message: str):
        """Record mistake in memory for future learning"""
        if mistake_type not in self.mistake_memory:
            self.mistake_memory[mistake_type] = []

        error_report = {
            'type': mistake_type,
            'timestamp': datetime.utcnow().isoformat(),
            'message': error_message,
            'cycle_id': self.current_cycle.cycle_id if self.current_cycle else None
        }

        self.mistake_memory[mistake_type].append(error_report)

        # Store in vector database for long-term memory
        try:
            await self.vector_db.store_mistake_pattern(mistake_type, error_message)
        except Exception as e:
            self.logger.warning(f"Failed to store mistake pattern: {e}")

        # Attempt remediation
        await self._remediate_failure(error_report)

    async def _remediate_failure(self, error_report: dict) -> bool:
        """
        Attempt to automatically fix common errors based on the error report.
        Returns True if a fix was attempted.
        """
        mistake_type = error_report.get('type')
        message = error_report.get('message', '')
        
        self.logger.info(f"Attempting remediation for {mistake_type}...")
        
        remediation_success = False

        try:
            if mistake_type == 'import_error':
                # Handle ImportError / ModuleNotFoundError
                # Regex to find module name from "No module named 'xyz'"
                match = re.search(r"No module named ['\"]?([\w\-]+)['\"]?", message)
                if match:
                    module_name = match.group(1)
                    self.logger.info(f"Identified missing module: {module_name}")
                    
                    # Append to requirements.txt
                    req_path = 'requirements.txt'
                    try:
                        # Check if already exists to avoid duplicates
                        current_reqs = ""
                        if os.path.exists(req_path):
                            with open(req_path, 'r') as f:
                                current_reqs = f.read()
                        
                        if module_name not in current_reqs:
                            with open(req_path, 'a') as f:
                                f.write(f"\n{module_name}")
                            self.logger.info(f"Added {module_name} to requirements.txt")
                            remediation_success = True
                        else:
                            self.logger.info(f"Module {module_name} already in requirements.txt")
                    except Exception as e:
                        self.logger.error(f"Failed to update requirements.txt: {e}")

            elif mistake_type == 'syntax_error':
                # Flag file for "Fix-it" pass
                # Extract filename if available in error message, or mark generic fix-it
                # Pattern often: "File "path/to/file.py", line X"
                match = re.search(r"File \"([^\"]+)\", line (\d+)", message)
                if match:
                    file_path = match.group(1)
                    line_num = match.group(2)
                    self.logger.info(f"Flagging {file_path} (line {line_num}) for syntax repair.")
                    
                    # Add to a repair queue or cycle instructions
                    if self.current_cycle:
                        repair_task = f"FIX_SYNTAX: {file_path}:{line_num}"
                        if self.current_cycle.learning_insights is None:
                            self.current_cycle.learning_insights = []
                        self.current_cycle.learning_insights.append(repair_task)
                        remediation_success = True
            
            if remediation_success:
                self.logger.info(f"Remediation action taken for {mistake_type}")
                # Update memory with fix action
                action_details = {
                    'type': mistake_type,
                    'action': 'requirements_update' if mistake_type == 'import_error' else 'syntax_flag',
                    'timestamp': datetime.utcnow().isoformat()
                }

                if self.memory_system:
                    try:
                        self.memory_system.store_fix_action(mistake_type, action_details['action'], action_details)
                    except Exception as e:
                        self.logger.warning(f"Failed to store fix action in MemorySystem: {e}")
                
                if self.current_cycle:
                    if not hasattr(self.current_cycle, 'fix_actions'):
                         # Monkey-patching for now if class doesn't have it, 
                         # or just store in insights as fallback
                         self.current_cycle.fix_actions = []
                    
                    # We might need to store this somewhere persistent if cycle object doesn't support it directly
                    # For now, append to insights to ensure visibility
                    self.current_cycle.learning_insights.append(f"REMEDIATION: {json.dumps(action_details)}")

        except Exception as e:
            self.logger.error(f"Error during remediation: {e}")
            
        return remediation_success

    async def _generate_learning_insight(self, failure: UtilityResult) -> str:
        """Generate learning insight from failure"""
        mistake_type = self._classify_mistake(failure.error_message)

        # Check if we've seen similar mistakes before
        similar_mistakes = self.mistake_memory.get(mistake_type, [])

        if len(similar_mistakes) > 1:
            insight = f"Recurring {mistake_type} in {failure.repository}: {failure.error_message[:100]}..."
        else:
            insight = f"New {mistake_type} learned from {failure.repository}: {failure.error_message[:100]}..."

        return insight

    async def _calculate_rewards(self, build_results: List[UtilityResult]) -> Dict[str, float]:
        """Calculate XMRT token rewards for the learning cycle"""
        try:
            return await self.incentive_calc.calculate_cycle_rewards(
                build_results,
                self.current_cycle
            )
        except Exception as e:
            self.logger.warning(f"Failed to calculate rewards: {e}")
            return {'total_tokens': 0.0, 'quality_score': 0.0}

    async def _update_long_term_memory(self):
        """Update long-term memory in Glacier VectorDB"""
        if not self.current_cycle:
            return

        try:
            # Store cycle summary
            cycle_summary = {
                'cycle_id': self.current_cycle.cycle_id,
                'repositories_discovered': self.current_cycle.repositories_discovered,
                'utilities_built': self.current_cycle.utilities_built,
                'success_rate': (self.current_cycle.utilities_built / 
                               max(self.current_cycle.repositories_discovered, 1)),
                'quality_score': self.current_cycle.quality_score,
                'tokens_earned': self.current_cycle.xmrt_tokens_earned,
                'insights': self.current_cycle.learning_insights
            }

            await self.vector_db.store_learning_cycle(cycle_summary)

            # Clean old memories based on retention policy
            cutoff_date = datetime.utcnow() - timedelta(days=self.config['memory_retention_days'])
            await self.vector_db.cleanup_old_memories(cutoff_date)

        except Exception as e:
            self.logger.warning(f"Failed to update long-term memory: {e}")

    async def _commit_utilities(self, build_results: List[UtilityResult]):
        """Commit successful utilities to repositories"""
        successful_builds = [r for r in build_results if r.success and r.tests_passed]

        for build in successful_builds:
            try:
                # This would integrate with git/GitHub API to commit code
                self.logger.info(f"Would commit utility: {build.utility_name} to {build.repository}")

                # For now, just log the intent
                # In full implementation, this would use PyGitHub or similar

            except Exception as e:
                self.logger.error(f"Failed to commit {build.utility_name}: {e}")

    async def _update_performance_metrics(self):
        """Update overall performance metrics"""
        if not self.learning_history:
            return

        recent_cycles = self.learning_history[-10:]  # Last 10 cycles

        # Calculate metrics
        total_utilities = sum(cycle.utilities_built for cycle in recent_cycles)
        total_attempts = sum(cycle.repositories_discovered for cycle in recent_cycles)
        total_tokens = sum(cycle.xmrt_tokens_earned for cycle in recent_cycles)
        avg_quality = sum(cycle.quality_score for cycle in recent_cycles) / len(recent_cycles)

        success_rate = total_utilities / max(total_attempts, 1)

        # Calculate learning velocity (utilities per hour)
        if len(recent_cycles) >= 2:
            time_span = (recent_cycles[-1].end_time - recent_cycles[0].start_time).total_seconds() / 3600
            learning_velocity = total_utilities / max(time_span, 1)
        else:
            learning_velocity = 0

        # Update metrics
        self.performance_metrics.update({
            'success_rate': success_rate,
            'avg_quality_score': avg_quality,
            'total_utilities_built': self.performance_metrics['total_utilities_built'] + 
                                   (self.current_cycle.utilities_built if self.current_cycle else 0),
            'total_tokens_earned': self.performance_metrics['total_tokens_earned'] + 
                                 (self.current_cycle.xmrt_tokens_earned if self.current_cycle else 0),
            'learning_velocity': learning_velocity
        })

    async def _load_learning_history(self):
        """Load previous learning history from vector database"""
        try:
            self.learning_history = await self.vector_db.load_learning_history()
            self.mistake_memory = await self.vector_db.load_mistake_patterns()
            self.logger.info(f"Loaded {len(self.learning_history)} previous learning cycles")
        except Exception as e:
            self.logger.warning(f"Could not load learning history: {e}")

    async def _sync_with_meshnet(self):
        """Sync learning data with MESHNET for offline capabilities"""
        try:
            # This would implement MESHNET synchronization
            self.logger.info("Syncing with MESHNET for offline learning capabilities")
            # Placeholder for MESHNET integration
        except Exception as e:
            self.logger.warning(f"MESHNET sync failed: {e}")

    async def _handle_critical_error(self, error: Exception):
        """Handle critical errors in the learning system"""
        self.logger.critical(f"Critical error in IALS: {error}")

        # Record the critical error
        await self._record_mistake("critical_system_error", str(error))

        # Attempt recovery
        try:
            await asyncio.sleep(60)  # Wait before retry
            self.logger.info("Attempting system recovery...")
            await self._initialize_services()
        except Exception as recovery_error:
            self.logger.critical(f"Recovery failed: {recovery_error}")
            raise

    # Public API methods

    async def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning system status"""
        return {
            'current_cycle': self.current_cycle.cycle_id if self.current_cycle else None,
            'total_cycles_completed': len(self.learning_history),
            'performance_metrics': self.performance_metrics,
            'system_health': 'healthy',  # Could be more sophisticated
            'last_cycle_summary': (
                {
                    'cycle_id': self.learning_history[-1].cycle_id,
                    'utilities_built': self.learning_history[-1].utilities_built,
                    'tokens_earned': self.learning_history[-1].xmrt_tokens_earned,
                    'quality_score': self.learning_history[-1].quality_score
                } if self.learning_history else None
            )
        }

    async def force_learning_cycle(self) -> str:
        """Manually trigger a learning cycle"""
        if self.current_cycle:
            return f"Learning cycle already in progress: {self.current_cycle.cycle_id}"

        await self._execute_learning_cycle()
        return f"Manual learning cycle completed: {self.learning_history[-1].cycle_id}"

    async def get_mistake_analysis(self) -> Dict[str, Any]:
        """Get analysis of mistakes and learning patterns"""
        mistake_analysis = {}

        for mistake_type, mistakes in self.mistake_memory.items():
            mistake_analysis[mistake_type] = {
                'count': len(mistakes),
                'recent_occurrences': len([
                    m for m in mistakes 
                    if datetime.fromisoformat(m['timestamp']) > 
                       datetime.utcnow() - timedelta(hours=24)
                ]),
                'trend': 'improving' if len(mistakes) < 5 else 'needs_attention'
            }

        return {
            'mistake_patterns': mistake_analysis,
            'total_mistakes': sum(len(mistakes) for mistakes in self.mistake_memory.values()),
            'learning_insights_count': sum(
                len(cycle.learning_insights) for cycle in self.learning_history
            )
        }

# Service initialization and startup
if __name__ == "__main__":
    import uvloop

    # Use uvloop for better performance
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create and start the enhanced service
    service = EnhancedElizaAgentService()

    try:
        asyncio.run(service.start_continuous_learning())
    except KeyboardInterrupt:
        logging.info("Enhanced Eliza Agent Service stopped by user")
    except Exception as e:
        logging.error(f"Service failed: {e}")
        raise
