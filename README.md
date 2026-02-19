# TIA-ADK Project

The `tia-adk` project provides a structured way to interface with Siemens TIA Portal Openness API, export PLC blocks as XML, and analyze them using an LLM Agent.

## Key Features
- **TIA Openness Integration**: Uses `pythonnet` to interface with Siemens Engineering DLLs.
- **LLM Agent**: Leverages OpenAI (or compatible APIs) to reason about PLC code in XML format.
- **Modern Tooling**: Managed by `uv` for fast dependency management and virtual environments.

## Project Structure
- `main.py`: CLI entry point.
- `src/openness.py`: TIA Portal connection and export logic.
- `src/agent.py`: AI Agent logic for code analysis.
- `src/utils.py`: Utility functions.

## How to Run

### 1. Installation
Ensure you have `uv` installed. 

> [!TIP]
> On Windows, if you encounter an error activating the virtual environment in PowerShell, run this command once to allow local scripts:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Then run:
```powershell
python -m uv sync
```

### 2. Exporting from TIA Portal
Ensure TIA Portal is running with a project open. Run:
```powershell
python -m uv run main.py export --output ./my_export
```
> [!NOTE]
> This requires TIA Portal Openness to be installed and the user to be in the "Siemens TIA Openness" user group.

### 3. Analyzing PLC Code
To analyze the exported XMLs with an LLM:
```powershell
python -m uv run main.py analyze --input ./my_export --api-key YOUR_OPENAI_API_KEY
```
For testing without an API key, you can use the `--mock` flag:
```powershell
python -m uv run main.py analyze --input ./tests/mock_data --mock
```

## Configuration
The default TIA Portal API path is set in `src/openness.py`. You have updated it to:
`C:\Program Files\Siemens\Automation\Portal V17\PublicAPI\V17`

## Next Steps
- [ ] Add support for SCL source code extraction to reduce token usage.
- [ ] Integrate with local LLMs (e.g. via Ollama).
- [ ] Implement automated build/test CI for the wrapper.
