"""
CLI interface for the Financial AI Assistant.

Usage:
    python main.py
    python main.py --model sonar-pro
    python main.py --data path/to/financial_data.csv
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from assistant import FinancialAssistant
from financial_analyzer import load_and_calculate

BANNER = """
╔══════════════════════════════════════════════════════╗
║         Financial AI Assistant  (2005–2024)          ║
╚══════════════════════════════════════════════════════╝
Type your question and press Enter.
Commands:  /reset  — clear conversation history
           /quit   — exit
"""

DIVIDER = "─" * 54


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Financial AI Assistant CLI")
    parser.add_argument(
        "--data",
        default="financial_data.csv",
        help="Path to financial data CSV (default: financial_data.csv)",
    )
    parser.add_argument(
        "--model",
        default="sonar",
        help="Perplexity model name (default: sonar)",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()

    args = parse_args()

    # Load and process financial data
    try:
        metrics = load_and_calculate(args.data)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Initialise assistant
    try:
        assistant = FinancialAssistant(metrics=metrics, model=args.model)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    print(BANNER)
    print(f"Loaded {len(metrics)} years of data ({metrics[0].year}–{metrics[-1].year}).")
    print(DIVIDER)

    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue

        if question.lower() in ("/quit", "/exit", "quit", "exit"):
            print("Goodbye!")
            break

        if question.lower() == "/reset":
            assistant.reset_history()
            print("Conversation history cleared.")
            continue

        print()
        try:
            answer = assistant.ask(question)
        except Exception as e:
            print(f"[API error] {e}", file=sys.stderr)
            continue

        print(f"Assistant:\n{answer}")
        print(DIVIDER)


if __name__ == "__main__":
    main()
