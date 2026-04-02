import os
from . import mcp
from pathlib import Path

additional_skills_roots: list[Path] = []

def get_skills_roots() -> list[Path]:
    roots = []
    roots.extend(additional_skills_roots)
                
    # Ensure fallback
    default_root = Path.home() / ".config" / "redwood_skills"
    default_root.mkdir(parents=True, exist_ok=True)
    if default_root not in roots:
        roots.append(default_root)
        
    return roots

@mcp.tool()
def list_available_skills() -> str:
    """
    Lists all available agent skills discovered on the system across all configured skill paths.
    Call this tool to discover what specialized instructions or skills are available to you.
    """
    skills = []
    roots = get_skills_roots()
    
    for root in roots:
        for skill_dir in root.iterdir():
            if skill_dir.is_dir():
                skill_path = skill_dir / "SKILL.md"
                if skill_path.exists():
                    skill_name = skill_dir.name
                    content = skill_path.read_text(encoding="utf-8", errors="replace")
                    
                    description = "No description provided."
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            for line in parts[1].splitlines():
                                if line.startswith("description:"):
                                    description = line.split("description:", 1)[1].strip()
                                    break
                    
                    skills.append(f"- **{skill_name}**: {description} (from {root})")
                    
    if not skills:
        return "No skills currently available in any configured directories."
        
    return "Available Skills:\n" + "\n".join(skills)

@mcp.tool()
def activate_skill(skill_name: str) -> str:
    """
    Activates and loads the full markdown instructions for a specific agent skill.
    Call this tool whenever you decide to use a skill from the <available_skills> catalog.
    """
    roots = get_skills_roots()
    for root in roots:
        skill_path = root / skill_name / "SKILL.md"
        if skill_path.exists():
            content = skill_path.read_text(encoding="utf-8", errors="replace")
            return f"<skill_content name=\"{skill_name}\">\n{content}\n</skill_content>"
            
    return f"Error: Skill '{skill_name}' not found in any configured paths."

@mcp.tool()
def add_skills_root(path: str) -> str:
    """
    Adds a new directory to the list of folders searched for agent skills.
    Use this tool to dynamically load skills from a given absolute path during the session.
    """
    p = Path(os.path.expanduser(path))
    if not p.exists():
        return f"Error: Path '{path}' does not exist."
    if not p.is_dir():
        return f"Error: Path '{path}' is not a directory."
        
    if p not in additional_skills_roots:
        additional_skills_roots.append(p)
        return f"Successfully added '{path}' to skills search paths."
    else:
        return f"Path '{path}' is already in the skills search paths."
