# Jupyter Notebook Editor Skill

> Before installing this skill, please note that this skill requires an external PyPi package `nbformat`. `codex` would try to install this package. In my testing, `codex` is very inconsistent in where it installs it (sometimes the python in the environment, sometimes creating a `.venv`, etc.). 
> I'm don't know how to bundle these dependencies in the skill or force codex to use a sandbox. If you have any suggestions, please help me by raising an issue.  

A codex skill to interact with jupyter notebooks. I was using codex for reviewing my jupyter notebooks for grammar and it had a lot of difficulty in working with the format (reading or editing cells in the notebook).  
This skill allows codex to use a packaged script to work with notebooks (allowing it to read/list/write specific cells).  

Example prompt that can work after you install this skill
```
Review this jupyter notebook <file> for grammar in markdown cells
```

## Installation
Clone this repository and copy the directory `jupyter-notebook-editor` in your `~/.codex/skills` directory.  

## Requirements
- Python 3.9+
- [`nbformat`](https://nbformat.readthedocs.io/) (install with `pip install nbformat`)

## How it works?
`scripts/nb_api.py` exposes a simple CLI to work with jupyter notebooks. It gives access to the commands `list,delete,update,insert,get` to work with cells inside notebooks individually.  
Check out `SKILL.md` to see the agent uses it.  

## Testing
Currently tested with only `gpt-5.1-codex medium`. Let me know if it doesn't work well with other models please.   

## Approvals
You need to allow `workspace-write`. It writes intermediate content to `/tmp`, you might get repeated update approval requests if you don't allow the above permission.  

## Repository Layout
- `jupyter-notebook-editor/SKILL.md` – authoritative instructions for agents using the skill.
- `jupyter-notebook-editor/scripts/nb_api.py` – CLI used for listing, reading, updating, deleting, and inserting notebook cells.
- `jupyter-notebook-editor/references/` – cheatsheets and worked examples covering common notebook operations and nbformat tips.

