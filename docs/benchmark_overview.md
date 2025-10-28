# Benchmark Overview

## Design Philosophy

HumanStudyBench is designed with three core principles:

### 1. Realistic
Studies are drawn from actual published research, not synthetic tasks. Agents must navigate the same complexities researchers face: ambiguous instructions, individual differences, and measurement noise.

### 2. Sustainable
The benchmark uses a modular structure where studies can be added incrementally. Automated validation ensures data quality, and version control tracks changes over time.

### 3. Systematic
Each study follows standardized schemas. Evaluation is automated via unit tests, ensuring reproducible and comparable results across different agents.

## What Makes a Good Unit Test?

In HumanStudyBench, each study is a unit test. A good study:

1. **Has Clear Specifications**: Complete experimental details
2. **Is Self-Contained**: All materials and instructions included
3. **Has Verifiable Outcomes**: Quantitative results that can be checked
4. **Is Reproducible**: Another researcher could replicate the study
5. **Is Well-Documented**: Proper citation and metadata

## Benchmark Structure

### Three-Layer Architecture

```
┌─────────────────────────────────────────┐
│         Studies (Data Layer)            │
│  - Metadata, Specs, Ground Truth        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Agents (Execution Layer)           │
│  - BaseAgent Interface                  │
│  - Custom Implementations               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Evaluation (Scoring Layer)          │
│  - Metrics, Validators, Scorers         │
└─────────────────────────────────────────┘
```

### Data Layer: Studies

Each study contains:
- **Metadata**: Bibliographic information, domain classification
- **Specification**: What needs to be replicated (design, procedure, materials)
- **Ground Truth**: Original results and validation criteria
- **Materials**: Stimuli, instructions, questionnaires

### Execution Layer: Agents

Agents implement the `BaseAgent` interface:
```python
class BaseAgent(ABC):
    @abstractmethod
    def run_study(self, specification: Dict) -> Dict:
        """Execute study and return results."""
        pass
```

Agents receive specifications and must return results in a standardized format.

### Evaluation Layer: Scoring

Studies are scored based on:
1. **Statistical Similarity**: How close are the results to original findings?
2. **Hypothesis Validation**: Are the key effects replicated?
3. **Effect Size Matching**: Are effect sizes in the expected range?

## Study Lifecycle

### 1. Curation
```
Published Paper → Extract Information → Structure Data → Validate
```

### 2. Integration
```
Create Study Directory → Add Files → Update Registry → Run Validation
```

### 3. Evaluation
```
Agent Runs Study → Results Compared → Tests Run → Score Computed
```

## Domains Covered

HumanStudyBench covers multiple domains of human research:

### Cognitive Psychology
- Attention and perception
- Memory and learning
- Decision making
- Problem solving

### Social Psychology
- Attitudes and persuasion
- Group dynamics
- Social cognition
- Prosocial behavior

### Behavioral Economics
- Choice under uncertainty
- Temporal discounting
- Fairness and cooperation
- Market behavior

### Developmental Psychology
- Cognitive development
- Social development
- Language acquisition

## Difficulty Levels

Studies are classified by difficulty:

### Easy
- Simple designs (e.g., 2x2 between-subjects)
- Clear-cut effects
- Minimal confounds
- Standard measures

### Medium
- Within-subjects or mixed designs
- Multiple dependent variables
- Some counterbalancing required
- Moderately complex analyses

### Hard
- Complex factorial designs
- Subtle effects or interactions
- Individual differences matter
- Advanced statistical methods

## Evaluation Metrics

### Primary Metric: Pass Rate
Percentage of validation tests passed. A study has multiple tests:
- Main effect present (p < .05)
- Effect direction correct
- Effect size in range
- Descriptive statistics similar

### Secondary Metrics
- **Statistical Similarity Score**: Correlation between agent and original results
- **Precision Score**: How tightly agent results match originals
- **Robustness**: Consistency across multiple runs

### Scoring Example

```python
Study Results:
- Main effect test: PASS (p = .002, expected p < .05)
- Direction test: PASS (agent: M_A > M_B, original: M_A > M_B)
- Effect size test: PASS (d = 1.8, expected range: [1.5, 2.5])
- Descriptive stats test: PARTIAL (within 15% of original)

Total Score: 3.5 / 4.0 = 87.5%
```

## Design Decisions

### Why JSON?
- Human-readable
- Easy to version control
- Schema validation
- Language agnostic

### Why One Directory Per Study?
- Modular
- Easy to add/remove
- Clear organization
- Parallel development

### Why Unit Test Paradigm?
- Familiar to developers
- Automated
- Scalable
- Clear pass/fail

### Why Manual Curation?
- Quality control
- Domain expertise
- Thoughtful selection
- Sustainable at scale

## Comparison to Other Benchmarks

| Feature | HumanStudyBench | BIG-bench | HELM | EleutherAI |
|---------|-----------------|-----------|------|------------|
| Domain | Human Studies | General AI | Language Models | Language Models |
| Tasks | Structured Studies | Diverse | Standardized | Standardized |
| Evaluation | Statistical Tests | Task-specific | Metrics Suite | Metrics Suite |
| Grounding | Published Research | Synthetic | Mixed | Mixed |
| Extensibility | High | High | Medium | Medium |

## Use Cases

### Research Applications
- Evaluate AI agents for behavioral research
- Study AI alignment with human behavior
- Test LLMs on psychological tasks
- Develop synthetic participants

### Educational Applications
- Teach research methods
- Demonstrate experimental design
- Practice statistical analysis
- Learn about replication

### Industry Applications
- User research automation
- Product testing with AI agents
- Market research simulation
- A/B testing optimization

## Future Directions

### Short-term
- Expand to 50+ studies
- Add more domains
- Improve evaluation metrics
- Build community

### Long-term
- Automated study extraction from papers
- OSF integration for continuous updates
- Multi-modal studies (images, videos)
- Cross-cultural studies
- Longitudinal studies

## Limitations

### Current Limitations
- Manual curation bottleneck
- Limited to published studies
- Text-based specifications
- Statistical validation only

### Inherent Challenges
- Replication crisis in psychology
- Individual differences
- Context-dependent effects
- Measurement validity

## Ethical Considerations

### Using AI as Participants
- When is it appropriate?
- What are the limitations?
- How to validate results?
- Transparency requirements

### Data Privacy
- Original data often aggregated
- Respect participant privacy
- Clear licensing
- Proper attribution

### Impact on Research
- Could reduce human participant burden
- But: important to validate carefully
- Not a replacement for all human studies
- Complementary tool for researchers

## Contributing to the Benchmark

We welcome contributions! See:
- [Paper Curation Guide](paper_curation_guide.md) for adding studies
- [API Reference](api_reference.md) for technical details
- [DEVELOPMENT.md](../DEVELOPMENT.md) for contributor guidelines

## References

Key papers on benchmark design, replication, and AI evaluation:

1. Open Science Collaboration (2015). Estimating the reproducibility of psychological science.
2. Raji et al. (2021). AI and the Everything in the Whole Wide World Benchmark.
3. Liang et al. (2022). Holistic Evaluation of Language Models (HELM).
4. BIG-bench collaboration (2022). Beyond the Imitation Game.

## Contact

Questions? Feedback? Reach out:
- GitHub Issues: [Report bugs or request features]
- GitHub Discussions: [Ask questions or share ideas]
- Email: your.email@example.com
