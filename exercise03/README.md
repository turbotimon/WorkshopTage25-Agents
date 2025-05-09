# Exercise 03 – **OpenStreetMap Agent** 🌐🧭

In the previous session you learned how an **MCP server** exposes external
functionality (maps, …) and how to attach one to an agent.
Your mission: **implement `OpenStreetMapAgent`** so our assistant can answer
location-based questions (nearby places, route directions, etc.).

---

## 1 Learning goals

* Write an **async setup factory** for an agent.
* Interact with the **MCP repository** to obtain a server handle.
* Register the new agent as a **tool** inside a larger multi-agent system.

---

## 2 Provided starter code

| File | Purpose | Editable? |
|------|---------|-----------|
| `exercise03/my_agents.py` | Agents scaffold – **TODOs live here** | ✅ |
| `exercise03/my_tools.py`  | Helper tools & `MCPServerRepository`  | Uncomment the code (see TODO comment) |
| other repo files          | Glue / utilities                      | 🔒 read-only |

---

## 3 Tasks

### 3.1 `OpenStreetMapAgent.setup()`

1. Call the `get_instance()` on `MCPServerRepository` to obtain the singleton.
2. Retrieve the server server with the key `openstreetmaps`.
3. Return `cls(...)` with
    * `name` - a meaningful agent name
    * `instructions` – one or two sentences describing its domain.
    * `tools` - the agent should still be able to think and ask for clarifications
    * `mcp_servers` - the retrieved MCPS server
    * `model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY"))`

### 3.2 Register the tool in **`triage_agent`**

- use `asyncio.run` on the `setup` method to await the agent setup and then use the returned agent as a tool.
- Make sure to use a meaningful tool description and name
- You might want to use the inspector or call `list_tools` to see what tools the server offers. Alternatively, look it up on the GitHub repository. This will help you craft a better tool description.

### 3.3 Uncomment the code in `MCPServerRepository`

- Uncomment the code as mentioned in the TODO comment in the `MCPServerRepository` in `my_tools.py`
- If you want to run the solution, you also need to uncomment it in the `solution_exercise03` folder


### 3.4  Testing and refinement

- Test out the agent with different instructions
- Use different prompts and see if the agent performs better or worse

### 3.4  Bonus:
- Search for another MCP tool and add it to the agent

---

## 4 Hints

* `MCPServerRepository` is **already implemented** – no need to touch it.
* Remember that `setup()` is **async**, but you call it synchronously in
    `triage_agent` via `asyncio.run(...)`.