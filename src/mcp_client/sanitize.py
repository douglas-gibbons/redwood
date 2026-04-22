from typing import Dict, Any, List
import logging
import re

logging.getLogger().handlers.clear()
logger = logging.getLogger(__name__)

ALLOWED_SCHEMA_KEYS = {'type', 'format', 'description', 'nullable', 'enum', 'properties', 'required', 'items'}

def resolve_refs(schema: Any, root_schema: Any) -> Any:
    """Inlines $ref definitions in a JSON schema."""
    if not isinstance(schema, dict):
        if isinstance(schema, list):
            return [resolve_refs(i, root_schema) for i in schema]
        return schema
        
    if '$ref' in schema:
        ref_path = schema['$ref']
        if isinstance(ref_path, str) and ref_path.startswith('#/$defs/'):
            def_name = ref_path.split('/')[-1]
            if '$defs' in root_schema and def_name in root_schema['$defs']:
                resolved = resolve_refs(root_schema['$defs'][def_name], root_schema)
                clean = {}
                if isinstance(resolved, dict):
                    clean.update(resolved)
                for k, v in schema.items():
                    if k != '$ref':
                        clean[k] = resolve_refs(v, root_schema)
                return clean
                
    clean = {}
    for k, v in schema.items():
        clean[k] = resolve_refs(v, root_schema)
    return clean

def clean_schema_recursive(schema: Any) -> Any:
    """Removes keys from a JSON schema that are not supported by the Gemini SDK."""
    if not isinstance(schema, dict):
        if isinstance(schema, list):
            return [clean_schema_recursive(i) for i in schema]
        return schema
        
    clean = {}
    for k, v in schema.items():
        if k in ALLOWED_SCHEMA_KEYS:
            if k == 'properties' and isinstance(v, dict):
                clean_props = {}
                for prop_name, prop_schema in v.items():
                    clean_props[prop_name] = clean_schema_recursive(prop_schema)
                clean[k] = clean_props
            elif k == 'type' and isinstance(v, list):
                types = [t for t in v if isinstance(t, str)]
                if "null" in types:
                    clean['nullable'] = True
                    types.remove("null")
                clean[k] = types[0] if types else "string"
            else:
                clean[k] = clean_schema_recursive(v)
    return clean

class DictTool(dict):
    """A dictionary that poses as a Tool with name and description properties for the chat engine."""
    @property
    def name(self):
        return self["function_declarations"][0]["name"]
        
    @property
    def description(self):
        return self["function_declarations"][0]["description"]

def sanitize_name(name):
    return re.sub(r"[^a-zA-Z0-9]", "", name)

def sanitize_tools(tools):
    logger.debug(f"Sanitizing {len(tools)} tools")
    st = []
    for tool in tools:
        try:
            if hasattr(tool, 'model_dump'):
                data = tool.model_dump(exclude_none=True)
            elif hasattr(tool, '__dict__'):
                data = tool.__dict__
            elif isinstance(tool, dict):
                data = tool
            else:
                data = dict(tool)
                
            name = data.get('name', '')
            description = data.get('description', 'No description provided.')
            if not description:
                description = 'No description provided.'
                
            input_schema = data.get('inputSchema', {})
            
            inlined_schema = resolve_refs(input_schema, input_schema)
            clean_schema = clean_schema_recursive(inlined_schema)
            
            if 'type' not in clean_schema:
                clean_schema['type'] = 'object'
                
            # Create a DictTool mimicking genai.types.Tool wrapper
            st.append(DictTool({
                "function_declarations": [
                    {
                        "name": name,
                        "description": description,
                        "parameters": clean_schema
                    }
                ]
            }))
        except Exception as e:
            name = getattr(tool, 'name', str(tool))
            logger.error(f"Error sanitizing tool {name}: {e}")
    return st
