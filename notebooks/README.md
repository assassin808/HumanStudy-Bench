# Notebooks

This directory contains Jupyter notebooks for interactive analysis and exploration.

## Available Notebooks

### Analysis Notebooks
- `analysis.ipynb` - Analyze benchmark results and agent performance
- `exploration.ipynb` - Explore studies and data interactively

## Usage

```bash
# Install Jupyter if not already installed
pip install jupyter

# Launch Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

## Creating New Notebooks

When creating new notebooks:
1. Follow the naming convention: `descriptive_name.ipynb`
2. Add clear markdown cells explaining each section
3. Include imports at the top
4. Save outputs for reproducibility (when appropriate)
5. Add notebook to this README

## Tips

- Use relative paths to access data: `../data/`
- Import from src: `from src.core.benchmark import HumanStudyBench`
- Restart kernel if you modify source code
