# AI Agents in Action: Building Smart, Open-Source LLM Workflows
This is the official repository of the [Open Source AI Workshop](https://www.ch-open.ch/open-source-ai-workshops/) with the above name that takes place on May 9, 2025 at Bern University of Applied Sciences, Brückenstrasse 73, 3005 Bern.

# First steps

## 1. Installing uv

Please install the package and project manager **uv** for Python. You can install it directly via pip:

```bash
pip install uv
```

Alternatively, follow one of the installation procedures described [here](https://docs.astral.sh/uv/getting-started/installation/).

## 2. Installing the dependencies

After you installed uv, you can  use the following command to install the required Python dependencies:

```bash
uv sync
```

# Repository structure

The repository is divided into three subdirectories: 

1. The directory `ui` includes a streamlit interface that you can use to interact with your agents. You might need to change what gets called in the interface based on the exercise that you are working on.
2. Under `agents` you will implement the code for your own agents. These agents will be called by the streamlit code.
3. The `exercises` directory includes the exercise instructions in the form of Markdown files.