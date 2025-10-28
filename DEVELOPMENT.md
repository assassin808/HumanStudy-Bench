# Development Documentation

**Project**: HumanStudyBench  
**Version**: 0.1.0  
**Last Updated**: October 27, 2025  
**Status**: Initial Setup

---

## 📋 Project Overview

HumanStudyBench is a benchmark for evaluating AI agents' ability to reproduce published human studies. The benchmark provides structured representations of classic and contemporary studies, allowing agents to attempt replication under realistic constraints.

### Core Components

1. **Data Layer**: Structured studies with metadata, specifications, and ground truth
2. **Evaluation Layer**: Metrics and validators for scoring agent performance
3. **Agent Interface**: Abstract base class for implementing custom agents
4. **Toolchain**: Scripts for validation, reporting, and study management

---

## 📁 Repository Structure

```
HS_bench/
├── README.md                    # Main project documentation
├── LICENSE                      # MIT License
├── DEVELOPMENT.md              # This file - development tracking
├── requirements.txt            # Python dependencies
├── setup.py                    # Package installation (legacy)
├── pyproject.toml             # Package configuration (modern)
│
├── .gitignore                 # Git ignore patterns
├── .github/                   # GitHub Actions CI/CD (future)
│
├── data/                      # Benchmark data
│   ├── registry.json          # Study index
│   ├── schemas/               # JSON schemas for validation
│   └── studies/               # Individual study directories
│
├── src/                       # Source code
│   ├── __init__.py
│   ├── core/                  # Core functionality
│   ├── evaluation/            # Evaluation metrics
│   ├── agents/                # Agent interfaces
│   ├── utils/                 # Utilities
│   └── visualization/         # Plotting tools
│
├── tests/                     # Unit tests
├── examples/                  # Usage examples
├── scripts/                   # Utility scripts
├── docs/                      # Documentation
├── notebooks/                 # Jupyter notebooks
└── results/                   # Evaluation results (gitignored)
```

---

## 🚀 Development Timeline

### Phase 1: Project Setup ✅ (October 27, 2025) - COMPLETED
- [x] Create project structure
- [x] Initialize core configuration files (README, LICENSE, requirements.txt, setup.py, pyproject.toml)
- [x] Set up .gitignore
- [x] Create comprehensive documentation (5 docs files)
- [x] Implement core modules (Study, Benchmark, BaseAgent, Scorer, Metrics)
- [x] Add example study (study_001 - Asch Conformity Experiment)
- [x] Create validation schemas (metadata, specification, ground_truth)
- [x] Implement LLM-as-Participant agent architecture
- [x] Create usage examples (2 example scripts)
- [x] Add validation scripts (validate_study.py, quick_test.py)
- [x] Verify installation and functionality

### Phase 2: Core Implementation ✅ (October 27, 2025) - COMPLETED
- [x] Implement `Study` class
- [x] Implement `HumanStudyBench` class  
- [x] Create evaluation metrics (MetricsCalculator)
- [x] Build validation system (Scorer)
- [x] Implement base agent interface (BaseAgent)
- [x] Implement LLMParticipantAgent and ParticipantPool
- [x] **Pass/Fail Evaluation System**
  - [x] Design two-level evaluation criteria (study-level + benchmark-level)
  - [x] Implement Study.evaluate_pass_status() with 70%/85%/100% thresholds
  - [x] Implement Benchmark.evaluate_benchmark_pass() with dual criteria (60% score + 50% pass rate)
  - [x] Add grade system: fail/pass/high_quality/perfect (study), fail/pass/good/excellent (benchmark)
  - [x] Update ground_truth.json with weights and critical flags
  - [x] Document evaluation criteria in README

### Phase 3: Testing & Validation (Planned)
- [ ] Write unit tests for core modules
- [ ] Create integration tests
- [ ] Validate with pilot studies
- [ ] Documentation review

### Phase 4: Initial Release (Planned)
- [ ] Curate 10-20 initial studies
- [ ] Complete documentation
- [ ] Add usage examples
- [ ] Set up CI/CD
- [ ] Public release v0.1.0

---

## 📝 Current Tasks

### Completed ✅
1. ✅ Project structure created
2. ✅ Core modules implemented
3. ✅ Documentation written
4. ✅ Example study added (Stroop Effect)
5. ✅ Installation verified
6. ✅ Basic testing functional

### Next Steps
1. Add more example studies (target: 10-20 for v0.1.0)
2. Implement additional evaluation metrics (Bayes Factor, equivalence testing)
3. Create visualization module for results plotting
4. Add utility modules (validators, parsers)
5. Write comprehensive unit tests
6. Set up CI/CD pipeline
7. Consider OSF API integration for automated study curation

---

## 🔧 Technical Decisions

### Data Format
- **Choice**: JSON for all structured data
- **Rationale**: 
  - Human-readable and version control friendly
  - Easy to validate with JSON Schema
  - Wide language support for future extensions
  - Efficient for moderate-sized datasets

### Study Granularity
- **Choice**: One directory per study
- **Rationale**:
  - Modular and easy to add/remove studies
  - Clear separation of concerns
  - Facilitates parallel development
  - Simplifies version control

### Evaluation Strategy
- **Choice**: Unit test paradigm with two-level pass/fail system
- **Rationale**:
  - Familiar concept for developers
  - Automated and reproducible
  - Scalable to large numbers of studies
  - Clear pass/fail criteria
- **Implementation**:
  - Study-level: 70% threshold with critical test enforcement
  - Benchmark-level: Dual criteria (60% score + 50% pass rate)
  - Prevents gaming via single-metric optimization
  - Grade system provides nuanced performance feedback

### Evaluation Thresholds
- **Study-Level**:
  - Pass: 70% (acceptable replication)
  - High Quality: 85% (excellent replication)
  - Perfect: 100% (exact match)
  - Critical tests must pass regardless of score
- **Benchmark-Level**:
  - Pass: 60% average score AND 50% pass rate
  - Good: 75% average score AND 65% pass rate
  - Excellent: 85% average score AND 80% pass rate
- **Rationale**: 
  - 70% study threshold balances rigor with realistic replication challenges
  - Dual benchmark criteria prevents gaming (can't optimize just score or pass rate)
  - Critical tests ensure core findings must replicate

### Python Version
- **Choice**: Python 3.8+ 
- **Rationale**:
  - Balance between modern features and compatibility
  - Type hints support
  - Widely adopted in research community

---

## 📊 Study Curation Status

### Target Domains
- Cognitive Psychology
- Social Psychology
- Behavioral Economics
- Developmental Psychology
- Neuroscience (behavioral tasks)

### Curation Criteria
1. **Completeness**: Full experimental details available
2. **Reproducibility**: Clear procedures and materials
3. **Results**: Quantitative outcomes reported
4. **Accessibility**: Materials available via OSF or similar
5. **Impact**: Classic or high-impact studies preferred

### Current Studies
- **Total**: 1 (target: 50 for v1.0)
- **Completed**: 
  - study_001: Stroop Effect (Stroop, 1935) - Cognitive Psychology, Easy

---

## 🐛 Known Issues & TODOs

### Critical
- [ ] Need to finalize JSON schema specifications
- [ ] Decide on statistical validation thresholds
- [ ] Define partial credit system for evaluation

### Important
- [ ] Add .gitignore file
- [ ] Set up pre-commit hooks for code quality
- [ ] Create contribution guidelines
- [ ] Add example data for testing

### Nice to Have
- [ ] GitHub Actions for automated testing
- [ ] Docker container for reproducible environment
- [ ] Web-based leaderboard
- [ ] Interactive visualization dashboard

---

## 📚 Design Patterns

### Study Loading
```python
# Lazy loading pattern for efficient memory usage
benchmark.load_study("study_001")  # Loads on demand
```

### Agent Interface
```python
# Abstract base class ensures consistency
class BaseAgent(ABC):
    @abstractmethod
    def run_study(self, specification: Dict) -> Dict:
        pass
```

### Validation
```python
# Schema-based validation for data integrity
validator = StudyValidator(schema_path)
validator.validate(study_data)
```

---

## 🔄 Versioning Strategy

### Benchmark Versions
- **Major**: Breaking changes to data format or API
- **Minor**: New studies added, backward compatible
- **Patch**: Bug fixes, documentation updates

### Study Versions
- Each study has internal version tracking
- Changes to studies create new versions
- Historical versions preserved for reproducibility

---

## 🤝 Collaboration Notes

### Adding New Studies
1. Create study directory: `data/studies/study_XXX/`
2. Add metadata.json, specification.json, ground_truth.json
3. Include materials in `materials/` subdirectory
4. Update `data/registry.json`
5. Run validation script: `python scripts/validate_study.py study_XXX`
6. Submit PR with study documentation

### Code Contribution
1. Fork repository
2. Create feature branch
3. Follow code style (Black formatting)
4. Add tests for new functionality
5. Update documentation
6. Submit PR

---

## 📖 References & Resources

### Similar Benchmarks
- BIG-bench (Google)
- HELM (Stanford)
- EleutherAI Eval Harness
- Hugging Face Evaluate

### Standards & Schemas
- JSON Schema: https://json-schema.org/
- Open Science Framework API: https://developer.osf.io/
- PsychDS: https://psych-ds.github.io/

### Literature
- Reproducibility in psychology research
- Open science best practices
- AI agent evaluation methodologies

---

## 📞 Contact & Feedback

**Maintainers**: [Your Name/Team]  
**Email**: your.email@example.com  
**Issues**: [GitHub Issues](https://github.com/yourusername/HS_bench/issues)  
**Discussions**: [GitHub Discussions](https://github.com/yourusername/HS_bench/discussions)

---

## 📜 Change Log

### v0.1.0-dev (October 27, 2025)
- ✅ Initial project structure created
- ✅ Core configuration files added (README, LICENSE, requirements.txt, setup.py, pyproject.toml, .gitignore)
- ✅ Documentation framework established (5 comprehensive docs)
- ✅ Planning and design phase completed
- ✅ Core modules implemented:
  - `src/core/`: Study, Benchmark, exceptions
  - `src/agents/`: BaseAgent, LLMParticipantAgent, ParticipantPool
  - `src/evaluation/`: Scorer, MetricsCalculator
- ✅ Data infrastructure created:
  - JSON schemas (metadata, specification, ground_truth)
  - Registry system
  - Example study (study_001 - Asch Conformity Experiment)
- ✅ Examples and scripts added:
  - 2 usage examples (LLM participant demos)
  - 2 utility scripts (validate_study.py, quick_test.py)
- ✅ Package installed and tested successfully
- ✅ **Pass/Fail Evaluation System Implemented**:
  - Added Study.get_pass_threshold() and Study.evaluate_pass_status()
  - Added Benchmark.evaluate_benchmark_pass() with dual criteria
  - Updated study_001 ground_truth.json with weights and critical flags
  - Added comprehensive evaluation criteria to README
  - Updated DEVELOPMENT.md with evaluation design decisions
- ✅ **LLM-as-Participant Architecture Implemented**:
  - Created LLMParticipantAgent (single participant with profile)
  - Created ParticipantPool (manages multiple participants)
  - Profile-based system prompts ("pretend you are...")
  - Support for both auto-generated and custom profiles
  - Simulation mode and real LLM API integration
  - Created comprehensive usage guide (llm_participant_agent_guide.md)
  - Updated all documentation to reflect new architecture
  - Removed deprecated RandomAgent and old examples

---

## 🎯 Success Metrics

### Short-term (v0.1.0)
- [ ] 10+ curated studies
- [ ] 2+ example agent implementations
- [ ] Full documentation coverage
- [ ] 80%+ test coverage

### Medium-term (v0.5.0)
- [ ] 50+ curated studies across 5 domains
- [ ] 5+ agent implementations
- [ ] Community contributions (3+ external PRs)
- [ ] Published technical report

### Long-term (v1.0.0)
- [ ] 100+ studies
- [ ] Established evaluation protocol
- [ ] Academic paper published
- [ ] Active research community

---

**Note**: This document is updated regularly to reflect the current state of development. Last manual update: October 27, 2025.
