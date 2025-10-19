# Contributing to DevFoundry

Thank you for your interest in contributing to DevFoundry! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Agent Development](#agent-development)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other contributors

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Public or private harassment
- Publishing others' private information
- Other conduct deemed inappropriate

---

## Getting Started

### Prerequisites

```bash
# Required
- Python 3.11+
- Node.js 18+
- Docker Desktop
- Git
- Google Cloud SDK

# Recommended
- VS Code with Python extension
- Postman or similar API testing tool
```

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/devfactory.git
cd devfactory

# Add upstream remote
git remote add upstream https://github.com/nimergulf/devfactory.git

# Verify remotes
git remote -v
```

---

## Development Setup

### 1. Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 2. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
vim .env
```

**Required Environment Variables**:
```bash
PROJECT_ID=your-gcp-project
REGION=us-central1
VERTEX_AI_LOCATION=us-central1
FIRESTORE_DATABASE=(default)
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### 3. Local Development Setup

```bash
# Start local Firestore emulator
gcloud emulators firestore start --host-port=localhost:8080

# In another terminal, set environment variables
export FIRESTORE_EMULATOR_HOST=localhost:8080

# Run orchestrator locally
python orchestrator/main.py
```

### 4. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=orchestrator --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run tests in watch mode
pytest-watch
```

---

## Contributing Guidelines

### Types of Contributions

We welcome the following types of contributions:

#### 🐛 Bug Reports
- Use GitHub Issues with the "bug" label
- Include clear title and description
- Provide steps to reproduce
- Include error messages and logs
- Specify your environment (OS, Python version, etc.)

#### 💡 Feature Requests
- Use GitHub Issues with the "enhancement" label
- Describe the feature and its benefits
- Provide use cases and examples
- Discuss potential implementation approach

#### 📝 Documentation
- Improve existing documentation
- Add examples and tutorials
- Fix typos and clarify language
- Translate documentation (future)

#### 🧪 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Test coverage improvements
- Refactoring

---

## Pull Request Process

### 1. Create a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements
- `chore/` - Maintenance tasks

### 2. Make Your Changes

**Code Style**:
```bash
# Python: Follow PEP 8
# Format code with black
black orchestrator/

# Sort imports
isort orchestrator/

# Lint with flake8
flake8 orchestrator/

# Type check with mypy
mypy orchestrator/
```

**Commit Messages**:
```
Format: <type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Example:
feat(agents): Add Developer Agent code generation capability
fix(orchestrator): Fix race condition in workflow execution
docs(readme): Update installation instructions
```

### 3. Write Tests

```python
# Example test structure
import pytest
from orchestrator.agents.product_agent import ProductAgent

class TestProductAgent:
    @pytest.fixture
    def agent(self):
        return ProductAgent()
    
    def test_analyze_concept_success(self, agent):
        # Arrange
        concept = "Build a REST API for task management"
        
        # Act
        result = agent.analyze_concept(concept)
        
        # Assert
        assert result.status == "success"
        assert "feature_map" in result.artifacts
        assert len(result.artifacts["feature_map"]) > 0
    
    def test_analyze_concept_invalid_input(self, agent):
        # Arrange
        concept = ""
        
        # Act & Assert
        with pytest.raises(ValueError):
            agent.analyze_concept(concept)
```

### 4. Update Documentation

- Update relevant markdown files in `/docs`
- Add docstrings to new functions/classes
- Update API documentation if applicable
- Add examples for new features

### 5. Run Quality Checks

```bash
# Run all checks
./scripts/quality-checks.sh

# Or manually:
black --check orchestrator/
isort --check orchestrator/
flake8 orchestrator/
mypy orchestrator/
pytest --cov=orchestrator --cov-fail-under=80
```

### 6. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create Pull Request
# Fill out the PR template completely
```

### PR Template

```markdown
## Description
[Clear description of the change]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #[issue-number]

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
- [ ] Coverage maintained/improved

## Screenshots (if applicable)
[Add screenshots for UI changes]
```

### 7. Code Review Process

- Maintainers will review your PR
- Address feedback and comments
- Make requested changes
- Push updates to the same branch
- PR will be merged when approved

---

## Agent Development

### Creating a New Agent

```python
# File: orchestrator/agents/my_new_agent.py

from typing import Dict, Any
from orchestrator.agents.base import Agent, AgentContext, AgentResult

class MyNewAgent(Agent):
    """
    Description of what this agent does.
    
    Inputs:
        - artifact_1: Description
        - artifact_2: Description
    
    Outputs:
        - result_1: Description
        - result_2: Description
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "MyNewAgent"
        self.version = "1.0.0"
    
    def validate_inputs(self, context: AgentContext) -> bool:
        """Validate required inputs are present"""
        required = ["artifact_1", "artifact_2"]
        return all(key in context.artifacts for key in required)
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute agent logic"""
        # Step 1: Load inputs
        artifact_1 = context.load_artifact("artifact_1")
        artifact_2 = context.load_artifact("artifact_2")
        
        # Step 2: Process with LLM
        prompt = self._build_prompt(artifact_1, artifact_2)
        response = await self.llm_client.generate(prompt)
        
        # Step 3: Parse and validate output
        result = self._parse_response(response)
        if not self.validate_outputs(result):
            raise ValueError("Invalid output generated")
        
        # Step 4: Store artifacts
        context.store_artifact("result_1", result["output_1"])
        context.store_artifact("result_2", result["output_2"])
        
        return AgentResult(
            status="completed",
            artifacts={"result_1": result["output_1"], "result_2": result["output_2"]},
            metadata={"execution_time": result["time"]}
        )
    
    def validate_outputs(self, result: Dict[str, Any]) -> bool:
        """Validate output quality"""
        # Add validation logic
        return True
    
    def _build_prompt(self, artifact_1: Any, artifact_2: Any) -> str:
        """Build LLM prompt"""
        return f"""
        You are an AI agent performing [specific task].
        
        Input 1: {artifact_1}
        Input 2: {artifact_2}
        
        Please provide:
        1. [Output requirement 1]
        2. [Output requirement 2]
        
        Format as JSON.
        """
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response"""
        # Add parsing logic
        return {}
```

### Testing Your Agent

```python
# File: tests/test_my_new_agent.py

import pytest
from orchestrator.agents.my_new_agent import MyNewAgent
from orchestrator.agents.base import AgentContext

@pytest.fixture
def agent():
    return MyNewAgent()

@pytest.fixture
def context():
    return AgentContext(
        workflow_id="test-workflow",
        project_id="test-project",
        artifacts={"artifact_1": "value1", "artifact_2": "value2"},
        requirements={},
        metadata={},
        previous_outputs=[]
    )

class TestMyNewAgent:
    def test_validate_inputs_success(self, agent, context):
        assert agent.validate_inputs(context) is True
    
    def test_validate_inputs_missing_artifact(self, agent):
        context = AgentContext(
            workflow_id="test",
            project_id="test",
            artifacts={"artifact_1": "value1"},  # Missing artifact_2
            requirements={},
            metadata={},
            previous_outputs=[]
        )
        assert agent.validate_inputs(context) is False
    
    @pytest.mark.asyncio
    async def test_execute_success(self, agent, context):
        result = await agent.execute(context)
        assert result.status == "completed"
        assert "result_1" in result.artifacts
        assert "result_2" in result.artifacts
```

---

## Testing Requirements

### Test Coverage Goals

- Overall coverage: **> 80%**
- New code coverage: **> 90%**
- Critical paths: **100%**

### Test Types

**Unit Tests**:
```python
# Test individual functions/methods in isolation
def test_function_returns_correct_value():
    result = my_function(input)
    assert result == expected
```

**Integration Tests**:
```python
# Test component interactions
@pytest.mark.integration
async def test_agent_workflow():
    workflow = WorkflowOrchestrator()
    result = await workflow.execute(["Agent1", "Agent2"])
    assert result.status == "completed"
```

**End-to-End Tests**:
```python
# Test complete user scenarios
@pytest.mark.e2e
def test_complete_generation_workflow():
    client = TestClient(app)
    response = client.post("/api/v1/workflows", json=workflow_request)
    assert response.status_code == 200
```

### Running Specific Test Types

```bash
# Unit tests only
pytest -m "not integration and not e2e"

# Integration tests
pytest -m integration

# E2E tests
pytest -m e2e

# Slow tests
pytest -m slow
```

---

## Documentation

### Documentation Standards

**Code Documentation**:
```python
def function_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Dict containing:
            - key1: Description of key1
            - key2: Description of key2
    
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer
    
    Examples:
        >>> result = function_name("test", 42)
        >>> print(result)
        {'key1': 'value1', 'key2': 'value2'}
    """
    pass
```

**Markdown Documentation**:
- Use clear headings and structure
- Include code examples
- Add diagrams where helpful (Mermaid, PlantUML)
- Keep language simple and concise
- Update table of contents

---

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Example: `1.2.3` → Major.Minor.Patch

### Creating a Release

1. Update version in `__version__.py`
2. Update CHANGELOG.md
3. Create release branch: `release/v1.2.3`
4. Run full test suite
5. Create PR to main
6. After merge, tag release: `git tag v1.2.3`
7. Push tag: `git push origin v1.2.3`
8. GitHub Actions will build and publish

---

## Questions or Need Help?

- **Slack**: devfoundry-community.slack.com
- **Email**: dev@devfoundry.com
- **Discussions**: https://github.com/nimergulf/devfactory/discussions
- **Office Hours**: Thursdays 2-3 PM UTC (Zoom link in Slack)

---

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Annual contributor spotlight

---

Thank you for contributing to DevFoundry! 🚀

**Together, we're building the future of software development.**
