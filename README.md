# Blog Writing Agent 📝

A LangGraph-based AI agent that automatically generates technical blog posts with optional web research.

## Features

- **Intelligent Routing**: Automatically determines if web research is needed based on the topic
- **Web Research**: Uses Tavily to gather up-to-date information when needed
- **Structured Planning**: Creates detailed outlines with goals, bullets, and word targets
- **Parallel Writing**: Multiple workers write sections concurrently for speed
- **Multiple Blog Types**: Supports explainers, tutorials, news roundups, comparisons, and system design posts
- **Citation Support**: Automatically cites sources when research is used

## Architecture
oFrjBqA6sthHv5OvrEkfWGdyb3FY7FYHrP5zdUY8usFEupXYqqER


```
┌─────────────┐
│    START    │
└──────┬──────┘
       │
┌──────▼──────┐
│   Router    │ ← Decides if research needed
└──────┬──────┘
       │
  ┌────┴────┐
  │         │
  ▼         ▼
┌────┐   ┌──────────┐
│Skip│   │ Research │ ← Tavily web search
└──┬─┘   └────┬─────┘
   │          │
   └────┬─────┘
        │
┌───────▼───────┐
│  Orchestrator │ ← Creates blog plan
└───────┬───────┘
        │
   Fan-out to N workers
        │
┌───┬───┼───┬───┐
│   │   │   │   │
▼   ▼   ▼   ▼   ▼
┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
│W│ │W│ │W│ │W│ │W│ ← Parallel section writing
└┬┘ └┬┘ └┬┘ └┬┘ └┬┘
 │   │   │   │   │
 └───┴───┼───┴───┘
         │
  ┌──────▼──────┐
  │   Reducer   │ ← Combines into final blog
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │     END     │
  └─────────────┘
```

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/blog-agent.git
cd blog-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Using pip

```bash
pip install blog-agent
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here  # Optional
   ```

### Getting API Keys

- **Groq API Key** (Required): Get it at [console.groq.com/keys](https://console.groq.com/keys)
- **Tavily API Key** (Optional, for research): Get it at [tavily.com](https://tavily.com/)

## Usage

### Python API

```python
from blog_agent import BlogAgent, run

# Using the class
agent = BlogAgent()
result = agent.run("Write a blog on Self Attention")

# Using the convenience function
result = run("Write a blog on RAG pipelines")

# Access the generated content
print(result["final"])

# Access the plan
print(result["plan"].blog_title)
print(result["plan"].tasks)
```

### Command Line

```bash
# Basic usage
blog-agent "Write a blog on Self Attention"

# With specific date (for news roundups)
blog-agent "AI news this week" --as-of 2025-01-29

# Save to specific file
blog-agent "Docker best practices" --output my_blog.md

# Quiet mode
blog-agent "Python async patterns" --quiet
```

## Research Modes

The agent automatically selects a research mode based on the topic:

| Mode | When Used | Research |
|------|-----------|----------|
| `closed_book` | Evergreen concepts (algorithms, fundamentals) | None |
| `hybrid` | Topics needing current examples | Light research |
| `open_book` | News roundups, "latest" topics | Heavy research |

## Blog Types

- **explainer**: Technical concept explanations
- **tutorial**: Step-by-step guides with code
- **news_roundup**: Current events and developments
- **comparison**: Tool/technology comparisons
- **system_design**: Architecture and design patterns

## Project Structure

```
blog_agent/
├── src/
│   └── blog_agent/
│       ├── __init__.py      # Package exports
│       ├── agent.py         # Main BlogAgent class
│       ├── cli.py           # Command line interface
│       ├── config.py        # Settings and configuration
│       ├── graph.py         # LangGraph definition
│       ├── llm.py           # LLM client
│       ├── models.py        # Pydantic models
│       ├── nodes.py         # Graph nodes
│       ├── prompts.py       # System prompts
│       ├── state.py         # State definition
│       └── tools.py         # Research tools
├── tests/                   # Test files
├── configs/                 # Configuration files
├── output/                  # Generated blogs
├── .env.example             # Example environment file
├── .gitignore
├── pyproject.toml           # Project metadata
└── README.md
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/ --fix
```

### Type Checking

```bash
mypy src/
```

## Example Output

Running:
```python
run("Write a blog on Self Attention")
```

Produces:
```
================================================================================
BLOG GENERATION COMPLETE
================================================================================
Topic: Write a blog on Self Attention
Mode: closed_book
Blog Kind: explainer
As-of Date: 2025-01-29
Sections Written: 8
  - Introduction to Self Attention (200 words)
  - How Self Attention Works (250 words)
  - The Math Behind Self Attention (300 words)
  ...
Total Characters: 12,450
================================================================================
```

## Troubleshooting

### "BadRequestError: Failed to call a function"
The LLM is struggling with structured output. Try:
1. Use a larger model: Set `LLM_MODEL=llama-3.3-70b-versatile` in `.env`
2. Reduce complexity of your topic

### "GROQ_API_KEY not set"
Make sure you've created a `.env` file with your API key.

### Research not working
Ensure `TAVILY_API_KEY` is set in your `.env` file.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
