
import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
from rich.panel import Panel
from src.openness import TiaOpenness
from src.agent import PLCAgent

console = Console()

def main():
    parser = argparse.ArgumentParser(description="TIA-ADK: TIA Portal Openness Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Export Command
    valid_parser = subparsers.add_parser("export", help="Export PLC blocks from TIA Portal")
    valid_parser.add_argument("--output", "-o", default="./export", help="Output directory for XML files")
    
    # Analyze Command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze exported XML files with LLM")
    analyze_parser.add_argument("--input", "-i", default="./export", help="Input directory containing XML files")
    analyze_parser.add_argument("--output", "-o", default="./analysis", help="Output directory for analysis results")
    analyze_parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"), help="OpenAI API Key")
    analyze_parser.add_argument("--mock", action="store_true", help="Use mock analysis for testing")

    args = parser.parse_args()

    if args.command == "export":
        console.print(Panel("Starting Export Process", style="bold green"))
        try:
            tia = TiaOpenness()
            tia.connect()
            tia.load_project()
            tia.export_plc_blocks(args.output)
            console.print(f"[bold green]Export completed to {args.output}[/bold green]")
        except Exception as e:
            import traceback
            console.print(f"[bold red]Error during export: {e}[/bold red]")
            traceback.print_exc()
            sys.exit(1)

    elif args.command == "analyze":
        console.print(Panel("Starting Analysis Process", style="bold blue"))
        try:
            agent = PLCAgent(api_key=args.api_key)
            agent.process_directory(args.input, args.output, mock=args.mock)
            console.print(f"[bold blue]Analysis completed. Results in {args.output}[/bold blue]")
        except Exception as e:
            import traceback
            console.print(f"[bold red]Error during analysis: {e}[/bold red]")
            traceback.print_exc()
            sys.exit(1)
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
