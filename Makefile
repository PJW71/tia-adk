.PHONY: help xml-from-tia analyse

help:
	@echo "Available commands:"
	@echo "  make xml-from-tia  - Export PLC blocks from TIA Portal to XML"
	@echo "  make analyse       - Analyze exported XML files using LLM"

xml-from-tia:
	uv run python main.py export

analyse:
	uv run python main.py analyze
