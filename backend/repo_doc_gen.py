import os
import logging
import json
from typing import Dict, Any

try:
    from groq import Groq
except ImportError:
    Groq = None
    
try:
    from dotenv import load_dotenv, find_dotenv
    # Find the nearest .env file, walking up the directory tree
    env_path = find_dotenv(usecwd=True)
    if not env_path:
        # Fallback to absolute path just in case
        env_path = r"e:\gen_ai_pro\.env"
    load_dotenv(env_path)
except ImportError:
    pass

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

client = None
if Groq and os.environ.get("GROQ_API_KEY"):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def call_llm(prompt: str) -> str:
    """
    Calls the Groq API to generate documentation.
    Falls back to an error message if the API key is not set.
    """
    if not client:
        logger.warning("GROQ_API_KEY not set. Using fallback placeholder.")
        return f"# API Key Required\n\n> **⚠️ AI Generation Disabled**\n> The `GROQ_API_KEY` environment variable is not set. Cannot generate real AI documentation.\n\n_Placeholder for requested prompt._"

    logger.debug("Sending prompt to Groq API...")
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a Senior Technical Writer. Output ONLY pure, structured Markdown without conversational filler or backticks wrapping the whole response."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant", # Or another fast/capable groq model like mixtral-8x7b-32768
            temperature=0.2,
        )
        
        text = response.choices[0].message.content
        if text:
            # Clean up potential codeblock wrappers
            text = text.strip()
            if text.startswith("```markdown"):
                text = text[11:].strip()
            elif text.startswith("```"):
                text = text[3:].strip()
                
            if text.endswith("```"):
                text = text[:-3].strip()
                
            return text
        else:
            return "# Generation Error\n\nEmpty response from Groq API."
            
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        return f"# API Error\n\nFailed to generate content: {e}"

def generate_documentation(parsed_code: Dict[str, Any]) -> str:
    """
    Constructs a detailed prompt from the parsed Python AST and sends it to the LLM
    to generate structured Markdown documentation.
    
    Args:
        parsed_code (dict): The dictionary returned from parse_code_file().
        
    Returns:
        str: The generated Markdown documentation.
    """
    file_name = parsed_code.get("file", "unknown_file")
    functions = parsed_code.get("functions", [])
    classes = parsed_code.get("classes", [])
    docstrings = parsed_code.get("docstrings", [])
    
    logger.info(f"Generating documentation for {file_name}")

    # Build context for the LLM
    context_lines = [
        f"You are a Senior Python Developer tasked with writing comprehensive, production-ready documentation for a file named `{file_name}`.\n",
        "Here is the structural information extracted from the file:\n"
    ]

    if classes:
        context_lines.append(f"- **Classes defined**: {', '.join(classes)}")
        
    if functions:
        context_lines.append(f"- **Functions defined**: {', '.join(functions)}")
        
    if docstrings:
        context_lines.append("\n**Extracted Docstrings Context**:")
        for doc in docstrings:
            dtype = doc.get("type", "unknown")
            dname = doc.get("name", "unknown")
            dtext = doc.get("docstring", "")
            context_lines.append(f"- {dtype.capitalize()} `{dname}`: {dtext}")

    context_lines.append("\n**Required Output Format**:")
    context_lines.append("You MUST return the output in pure Markdown format. Follow this exact structure:")
    context_lines.append("""
# File: [File Name]

## 🎯 Purpose
[Provide a high-level summary of what this file does based on the provided context]

## 🧩 Components

### Classes
[Use a Markdown table to list class names and their purpose, if any]

### Functions
[Use a Markdown list with bolded names to explain the functions]

## 🚀 Usage
[Provide a brief, valid Python code example showing how someone might import and use this file with a `python` code block]
""")

    # Combine into the final prompt
    prompt = "\n".join(context_lines)
    logger.debug("Prompt construction complete. Sending to LLM.")

    # Send to the (currently mocked) LLM
    markdown_output = call_llm(prompt)
    
    logger.info(f"Successfully generated Markdown documentation for {file_name}")
    return markdown_output

def generate_file_fallback(parsed_code: Dict[str, Any]) -> str:
    """
    Generates a fallback Markdown documentation file if no classes or functions are found.
    Passes up to the first 50 lines of the file as an excerpt for the LLM to read.
    """
    file_name = parsed_code.get("file", "unknown_file")
    imports = parsed_code.get("imports", [])
    excerpt = parsed_code.get("excerpt", "")
    
    logger.info(f"Generating fallback generic documentation for {file_name}")
    
    context_lines = [
        f"Write a professional Markdown summary for the file `{file_name}`.",
        f"It contains no recognized structural classes or functions, but has the following imports: {', '.join(imports) if imports else 'None'}.",
        "Make an educated guess about its purpose based on its name, imports, and the following code excerpt.",
    ]
    
    if excerpt:
        context_lines.append("\n**File Excerpt (Top 50 Lines)**:")
        context_lines.append("```")
        context_lines.append(excerpt)
        context_lines.append("```")
        
    context_lines.extend([
        "\n**Required Output Section Format**:",
        "- **🎯 File Purpose**: A concise summary of what this file does based on the excerpt.",
        "- **📦 Detected Dependencies**: A bulleted list of potential dependencies or imports.",
        "Ensure the formatting looks professional and clean. Do not hallucinate classes if there are none."
    ])
    
    prompt = "\n".join(context_lines)
    return call_llm(prompt)

def generate_directory_summary(directory_name: str, files_in_dir: list) -> str:
    """
    Generates a Markdown summary for a specific directory and the files it contains.
    """
    logger.info(f"Generating directory summary for {directory_name}")
    
    context_lines = [
        f"Write a comprehensive Markdown documentation summary for the directory `{directory_name}`.",
        f"It contains the following documented files: {', '.join(files_in_dir)}",
        "Explain what role this directory likely plays in the overall architecture.",
        "## 📂 Directory Contents",
        "Create a Markdown table listing each file and a brief 1-sentence description of its expected purpose."
    ]
    
    prompt = "\n".join(context_lines)
    return call_llm(prompt)

def generate_project_overview(repo_url: str, total_files: int, detected_extensions: set, directories: set) -> str:
    """
    Generates the root index.md summarizing the whole project.
    Uses a highly structured, professional developer documentation format.
    """
    logger.info(f"Generating project overview for {repo_url}")
    
    context_lines = [
        "You are a senior software architect and technical documentation writer.",
        f"Generate professional developer documentation for the repository: `{repo_url}`.",
        "The output must resemble modern developer product documentation similar to Stripe, Vercel, or Kubernetes docs.",
        "\n**CRITICAL RULES:**",
        "1. Output must be **pure Markdown**.",
        "2. Keep explanations **short and precise**.",
        "3. Maximum **3 bullet points per section**.",
        "4. Each description must be **one short sentence**.",
        "5. Avoid generic architecture descriptions.",
        "6. Do NOT invent components like 'User Interface' or 'Database' unless they actually exist.",
        "7. Only describe components **present in the repository**.",
        "8. If a section has no data, **remove the entire section**.",
        "   - Examples:",
        "     * If there are no modules -> remove 'Modules'.",
        "     * If there are no directories -> remove directory section.",
        "     * If there are no classes/functions -> remove API section.",
        "     * If GitHub links are unavailable -> remove source links section.",
        f"\n**Context Data:**",
        f"- Total files analyzed: {total_files}",
        f"- Languages detected: {', '.join(detected_extensions)}",
        f"- Main mapped directories: {', '.join(directories)}",
        "\nGenerate documentation in the *exact* following structure:",
        "\n# Project Overview",
        "Write a 2-3 line description explaining the purpose of the repository.",
        "\n---",
        "\n# Hero Section",
        "Create a short product-style introduction. Include one tagline and 3 key features.",
        "\n---",
        "\n# System Architecture",
        "## Architecture Diagram",
        "Generate a clean Mermaid architecture diagram representing the real system workflow.",
        "IMPORTANT — MERMAID SYNTAX RULES:",
        "* Layout: `flowchart LR`",
        "* Arrows: Use ONLY dotted arrows without labels: `A -.-> B`",
        "* FORBIDDEN: `-->`, `-->|label|>`, `-.->|label|>`, or any `|>` suffix",
        "* FORBIDDEN: Any arrow with a `|...|>` label ending in `>`",
        "* CORRECT: `NodeA -.-> NodeB` (no label, no `>`)",
        "* Styles go at the bottom, nodes ONLY: `style NodeA fill:#1e1e1e,stroke:#666,stroke-width:1px,color:#fff`",
        "* NEVER apply style to arrows",
        "* Example of a valid diagram:",
        "```",
        "flowchart LR",
        "  subgraph Layer1",
        "    A[HTML]",
        "  end",
        "  subgraph Layer2",
        "    B[JavaScript]",
        "  end",
        "  A -.-> B",
        "  style A fill:#1e1e1e,stroke:#666,stroke-width:1px,color:#fff",
        "  style B fill:#1e1e1e,stroke:#666,stroke-width:1px,color:#fff",
        "```",
        "* Use **layered subgraphs**",
        "* Only include components that exist in the repository",
        "* If some layers do not exist, remove those layers.",
        "\n## How the Architecture Works",
        "Write 3-5 paragraphs explaining the overall design and how the components interact. Cover the reasoning behind the architecture decisions.",
        "\n\n# Key Components",
        "For each of the 3 most important components: write the name as a subheading and provide 2-3 sentences explaining its purpose, how it fits into the system, and why it is relevant.",
        "\n---",
        "\n# Data Flow",
        "Describe the data flow through the system in detail. For each step, explain **what happens**, **why it happens**, and **what the output is**. Use 5-7 steps with full sentences.",
        "\n---",
        "\n# Module Dependency Graph",
        "If multiple modules exist, generate a Mermaid dependency diagram (`flowchart LR`). Connect nodes using dotted arrows ONLY (`A -.-> B`). Apply dark theme styling ONLY to nodes (`style NodeName fill:#1e1e1e,stroke:#666,stroke-width:1px,color:#fff`). Only include this section if modules exist.",
        "\n---",
        "\n# API Reference",
        "If classes or functions exist, generate short API documentation. Format: ## Function: name(), Description:, Parameters:, Returns:. Only include if applicable.",
        "\n---",
        "\n# GitHub Source Links",
        f"If repository URLs exist, provide links to important files (e.g. {repo_url}/blob/main/...). Only include this section if links are available.",
        "\nFINAL OUTPUT REQUIREMENTS:",
        "* Clean Markdown formatting",
        "* Professional developer documentation style",
        "* Accurate repository-specific information",
        "* No generic diagrams",
        "* No unnecessary text"
    ]
    
    prompt = "\n".join(context_lines)
    return call_llm(prompt)

def generate_architecture_overview(directories: set, structure_mapping: dict) -> str:
    """
    Generates the architecture.md file explaining the folder structure.
    Uses layered flowchart LR Mermaid diagrams.
    """
    logger.info("Generating architecture overview")
    
    structure_text = "\n".join([f"- **{d}/**: {len(files)} files" for d, files in structure_mapping.items()])
    
    context_lines = [
        "You are a senior software architect generating the **Architecture section only** for a software repository.",
        "Your goal is to produce **clean, precise architecture diagrams** using Mermaid that reflect the **actual components in the repository**.",
        "\n**CRITICAL MERMAID SYNTAX RULES (MUST FOLLOW EXACTLY):**",
        "1. Output **Markdown only**.",
        "2. Generate **exactly one architecture diagram**.",
        "3. The diagram must use **flowchart LR** layout.",
        "4. Arrows: use ONLY `A -.-> B` format. NO labels on arrows.",
        "5. FORBIDDEN arrow forms: `-->`, `-->|label|`, `-->|label|>`, `-.-|label|>`, any form with `|>` at the end.",
        "6. CORRECT: `NodeA -.-> NodeB` — simple dotted arrow, no label, no trailing `>`.",
        "7. Apply dark theme styling ONLY to nodes using exactly: `style NodeName fill:#1e1e1e,stroke:#666,stroke-width:1px,color:#fff`",
        "8. Use **grouped layers (subgraphs)** to make diagrams visually organized.",
        "9. Use **real repository components only** based on the provided mapped directories.",
        "10. Do NOT generate generic diagrams.",
        "11. Here is a valid example:",
        "```",
        "flowchart LR",
        "  subgraph Input",
        "    A[Source]",
        "  end",
        "  subgraph Processing",
        "    B[Parser]",
        "  end",
        "  A -.-> B",
        "  style A fill:#1e1e1e,stroke:#666,stroke-width:1px,color:#fff",
        "  style B fill:#1e1e1e,stroke:#666,stroke-width:1px,color:#fff",
        "```",
        "\n**Context Data (Mapped Directories):**",
        structure_text,
        "\nGenerate the Markdown using the exact following structure:",
        "\n# Architecture",
        "## Overview",
        "Write 3-4 paragraphs explaining the architectural philosophy of this repository: what pattern it follows (e.g., layered, event-driven, monolithic), why it was likely chosen, and what trade-offs it involves.",
        "## Architecture Diagram",
        "Generate a high-level `flowchart LR` Mermaid system architecture diagram showing the core pipeline and data flow.",
        "Use layers/subgraphs based closely on the provided directory structure to logically group components.",
        "## Component Descriptions",
        "For each subgraph/layer in the diagram, write a dedicated subsection (### LayerName) with 2-3 sentences explaining its responsibilities and how it interacts with adjacent layers.",
        "## Design Decisions",
        "Write 2-3 bullet points explaining key design decisions inferred from the structure (e.g., separation of concerns, statelessness, file-based config).",
        "\nFINAL OUTPUT REQUIREMENTS:",
        "* Output pure Markdown.",
        "* Exactly 1 Mermaid diagram.",
        "* No generic explanations."
    ]
    
    prompt = "\n".join(context_lines)
    return call_llm(prompt)

def generate_modules_overview(directories: set, structure_mapping: dict) -> str:
    """
    Generates the modules.md file explaining the main components.
    """
    logger.info("Generating modules overview")
    
    structure_text = "\n".join([f"- **{d}/**: {len(files)} files" for d, files in structure_mapping.items()])
    
    context_lines = [
        "You are a senior software engineer writing a **Modules Reference** page.",
        "Based on the following repository structure, list the main modules and directories in a clear, concise bulleted list.",
        "Explain the theoretical responsibility of each directory.",
        "\n**Context Data (Mapped Directories):**",
        structure_text,
        "\nGenerate the Markdown using the exact following structure:",
        "\n# Modules",
        "## Overview",
        "Write 2-3 paragraphs explaining how the codebase is organized into modules, what naming conventions appear to be followed, and why this structure aids maintainability.",
        "## Core Components",
        "For each detected directory/module, write a subsection (### module_name/) with:",
        "- A 1-sentence summary of its responsibility.",
        "- 2-3 sentences explaining the design rationale for isolating this concern.",
        "- A list of typical files it might contain.",
        "\nFINAL OUTPUT REQUIREMENTS:",
        "* Output pure Markdown.",
        "* No conversational filler."
    ]
    
    prompt = "\n".join(context_lines)
    return call_llm(prompt)

def generate_api_overview(total_files: int, directories: set) -> str:
    """
    Generates the api_reference.md file.
    """
    logger.info("Generating API reference overview")
    
    context_lines = [
        "You are a senior technical writer creating an **API Reference** overview.",
        "Based on the project structure, provide a brief overview of the main APIs, classes, or entry points that a developer might interact with.",
        f"\n**Context Data:**",
        f"- Total files analyzed: {total_files}",
        f"- Main mapped directories: {', '.join(directories)}",
        "\nGenerate the Markdown using the exact following structure:",
        "\n# API Reference",
        "## Overview",
        "Write 2-3 paragraphs explaining the typical API surface of a project with this structure: what kinds of interfaces it exposes (functions, classes, events), how a developer would typically integrate with it, and what conventions to expect.",
        "## Main Interfaces",
        "For each identified interface area, write a subsection (### Area) with:",
        "- A description of the interface purpose.",
        "- 2-3 example entry points (class or function names) with brief descriptions.",
        "- A note on parameters or return values where relevant.",
        "## Usage Guidelines",
        "Write 3-4 bullet points with practical advice for a developer consuming this API for the first time.",
        "\nFINAL OUTPUT REQUIREMENTS:",
        "* Output pure Markdown.",
        "* Do not hallucinate exact function signatures if they are unknown, focus on component interfaces.",
        "* No conversational filler."
    ]
    
    prompt = "\n".join(context_lines)
    return call_llm(prompt)

if __name__ == "__main__":
    # Small test case simulating the parsed AST input from Step 3
    mock_parsed_code = {
        "file": "auth.py",
        "functions": [
            "__init__",
            "login_user",
            "logout_user"
        ],
        "classes": [
            "AuthManager"
        ],
        "docstrings": [
            {
                "type": "module",
                "name": "auth.py",
                "docstring": "This is a module level docstring."
            },
            {
                "type": "class",
                "name": "AuthManager",
                "docstring": "Manages user authentication lifecycle."
            },
            {
                "type": "function",
                "name": "login_user",
                "docstring": "Logs the user in."
            }
        ]
    }
    
    print(f"Testing Documentation Generation for: {mock_parsed_code['file']}...\n")
    
    # Generate the Markdown
    result = generate_documentation(mock_parsed_code)
    
    print("-" * 40)
    print("OUTPUT MARDOWN:")
    print("-" * 40)
    print(result)
