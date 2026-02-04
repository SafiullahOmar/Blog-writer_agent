"""
Command Line Interface for the Blog Writing Agent.

Usage:
    blog-agent "Write a blog on Self Attention"
    blog-agent "AI news this week" --as-of 2025-01-29
    blog-agent "RAG best practices" --output my_blog.md
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from blog_agent.agent import BlogAgent


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="blog-agent",
        description="Generate technical blog posts using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate a blog about a technical concept
    blog-agent "Write a blog on Self Attention"
    
    # Generate a news roundup for a specific date
    blog-agent "AI news this week" --as-of 2025-01-29
    
    # Save to a specific file
    blog-agent "RAG pipelines explained" --output rag_blog.md
    
    # Quiet mode (no progress output)
    blog-agent "Docker best practices" --quiet
        """,
    )
    
    parser.add_argument(
        "topic",
        type=str,
        help="The topic for the blog post",
    )
    
    parser.add_argument(
        "--as-of",
        type=str,
        default=None,
        help="Date for the blog (ISO format: YYYY-MM-DD). Defaults to today.",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (overrides default naming)",
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output",
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 0.1.0",
    )
    
    args = parser.parse_args()
    
    # Validate as-of date if provided
    if args.as_of:
        try:
            date.fromisoformat(args.as_of)
        except ValueError:
            print(f"Error: Invalid date format '{args.as_of}'. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)
    
    try:
        # Run the agent
        agent = BlogAgent()
        result = agent.run(
            topic=args.topic,
            as_of=args.as_of,
            verbose=not args.quiet,
        )
        
        # Handle custom output path
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result["final"], encoding="utf-8")
            if not args.quiet:
                print(f"Blog saved to: {output_path}")
        
        # Print the final content to stdout if quiet
        if args.quiet:
            print(result["final"])
            
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
