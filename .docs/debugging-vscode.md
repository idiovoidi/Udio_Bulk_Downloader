# VS Code Debugging

## Common Issue
Don't press F5 when `launch.json` is open - VS Code will try to run it as Python.

## How to Debug

**Method 1: Debug Panel**
1. Open a Python file
2. Click Debug icon (left sidebar)
3. Select config from dropdown
4. Press F5

**Method 2: Quick Debug**
1. Open any Python file
2. Press F5
3. Select "Python: Current File"

## Available Configs
- **Python: Current File** - Debug active file
- **Python: Udio Status** - Run `status` command
- **Python: Test Full Workflow** - Run full test

## Run Without Debugging
```bash
python test_full_workflow.py
python -m udio_downloader status
```
