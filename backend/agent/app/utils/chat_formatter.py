import json
from typing import Any, List, Dict, Optional


def format_chat_history(history: List[Any]) -> List[Dict]:
    """
    Format chat history into a clean, readable structure.
    
    Extracts meaningful information from complex objects like UserContent and Parts,
    and formats them in a human-readable way.
    
    Args:
        history: List of chat history items
        
    Returns:
        List of formatted message dictionaries
    """
    if not history:
        return []
    
    formatted_messages = []
    
    for item in history:
        try:
            if isinstance(item, dict):
                formatted_item = _format_dict_item(item)
            else:
                formatted_item = _format_history_item(item)
                
            if formatted_item:
                formatted_messages.append(formatted_item)
        except Exception as e:
            formatted_messages.append({
                "role": "unknown",
                "content": f"Error processing item: {str(e)[:100]}",
                "raw": str(item)[:200] + "..." if len(str(item)) > 200 else str(item)
            })
    
    return formatted_messages


def _format_dict_item(item: Dict) -> Optional[Dict]:
    """
    Format a dictionary item (which is what we get from the chat history).
    
    Args:
        item: Dictionary representing a chat message
        
    Returns:
        Formatted dictionary or None if item is empty
    """
    if not item:
        return None
    
    role = item.get('role', 'unknown')
    content = item.get('content', [])
    
    formatted_content = []
    
    if isinstance(content, list):
        for content_item in content:
            if isinstance(content_item, dict):
                content_type = content_item.get('type', 'unknown')
                
                if content_type == 'text':
                    formatted_content.append({
                        "type": "text",
                        "text": content_item.get('text', '')
                    })
                elif content_type == 'function_call':
                    formatted_content.append({
                        "type": "function_call",
                        "name": content_item.get('name', ''),
                        "args": content_item.get('args', {})
                    })
                elif content_type == 'function_response':
                    response_data = content_item.get('response', '')
                    parsed_response = _clean_response_data(response_data)
                    formatted_content.append({
                        "type": "function_response",
                        "name": content_item.get('name', ''),
                        "response": parsed_response
                    })
                else:
                    formatted_content.append(content_item)
            else:
                formatted_content.append({"type": "raw", "content": str(content_item)})
    else:
        formatted_content = [{"type": "raw", "content": str(content)}]
    
    return {
        "role": role,
        "content": formatted_content
    }


def _format_history_item(item: Any) -> Optional[Dict]:
    """
    Format a single history item into a clean structure.
    
    Args:
        item: Single chat history item
        
    Returns:
        Formatted dictionary or None if item is empty
    """
    if not hasattr(item, '__dict__'):
        return {"content": str(item)}
    
    item_dict = item.__dict__
    role = item_dict.get('role', 'unknown')
    
    parts = item_dict.get('parts', [])
    
    if isinstance(parts, str):
        parts_content = _extract_parts_from_string(parts)
    elif isinstance(parts, list):
        parts_content = _extract_parts_from_list(parts)
    else:
        parts_content = [{"type": "unknown", "content": str(parts)}]
    
    formatted_item = {
        "role": role,
        "content": parts_content
    }
    
    return formatted_item


def _extract_parts_from_string(parts_str: str) -> List[Dict]:
    """Extract meaningful content from string representation of parts."""
    content = []
    
    if "text='" in parts_str:
        text_start = parts_str.find("text='") + 6
        text_end = parts_str.find("')", text_start)
        if text_end > text_start:
            text = parts_str[text_start:text_end]
            content.append({
                "type": "text",
                "text": text
            })
    
    if "function_call=" in parts_str and "FunctionCall(" in parts_str:
        func_content = _extract_function_call_from_string(parts_str)
        if func_content:
            content.append(func_content)
    
    if "function_response=" in parts_str and "FunctionResponse(" in parts_str:
        resp_content = _extract_function_response_from_string(parts_str)
        if resp_content:
            content.append(resp_content)
    
    return content if content else [{"type": "empty", "content": "No extractable content"}]


def _extract_parts_from_list(parts_list: List) -> List[Dict]:
    """Extract meaningful content from list of parts objects."""
    content = []
    
    for part in parts_list:
        if hasattr(part, '__dict__'):
            part_dict = part.__dict__
            
            if part_dict.get('text'):
                content.append({
                    "type": "text",
                    "text": part_dict['text']
                })
            
            if part_dict.get('function_call'):
                func_call = part_dict['function_call']
                if hasattr(func_call, '__dict__'):
                    content.append({
                        "type": "function_call",
                        "name": getattr(func_call, 'name', 'unknown'),
                        "args": getattr(func_call, 'args', {})
                    })
            
            if part_dict.get('function_response'):
                func_resp = part_dict['function_response']
                if hasattr(func_resp, '__dict__'):
                    resp_data = getattr(func_resp, 'response', {})
                    content.append({
                        "type": "function_response",
                        "name": getattr(func_resp, 'name', 'unknown'),
                        "response": _clean_response_data(resp_data)
                    })
        else:
            content.append({
                "type": "unknown_part",
                "content": str(part)[:100] + "..." if len(str(part)) > 100 else str(part)
            })
    
    return content if content else [{"type": "empty", "content": "No parts found"}]


def _extract_function_call_from_string(parts_str: str) -> Optional[Dict]:
    """Extract function call information from string."""
    try:
        name_start = parts_str.find("name='") + 6
        name_end = parts_str.find("'", name_start)
        func_name = parts_str[name_start:name_end] if name_end > name_start else "unknown"
        
        args_start = parts_str.find("args={")
        if args_start > -1:
            brace_count = 0
            args_end = args_start + 5
            
            for i in range(args_start + 5, len(parts_str)):
                char = parts_str[i]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    if brace_count == 0:
                        args_end = i
                        break
                    brace_count -= 1
            
            args_str = parts_str[args_start+5:args_end]
            
            try:
                import ast
                args_dict = ast.literal_eval('{' + args_str + '}')
                return {
                    "type": "function_call",
                    "name": func_name,
                    "args": args_dict
                }
            except:
                return {
                    "type": "function_call",
                    "name": func_name,
                    "args": args_str
                }
    except:
        pass
    
    return None


def _extract_function_response_from_string(parts_str: str) -> Optional[Dict]:
    """Extract function response information from string."""
    try:
        name_start = parts_str.find("name='") + 6
        name_end = parts_str.find("'", name_start)
        func_name = parts_str[name_start:name_end] if name_end > name_start else "unknown"
        
        response_start = parts_str.find("response=")
        if response_start > -1:
            response_content_start = response_start + 9
            
            if parts_str[response_content_start:response_content_start+2] == "{'":
                brace_count = 0
                response_end = response_content_start
                in_string = False
                escape_next = False
                
                for i in range(response_content_start, len(parts_str)):
                    char = parts_str[i]
                    if escape_next:
                        escape_next = False
                        continue
                    if char == '\\':
                        escape_next = True
                        continue
                    if char == "'" and not escape_next:
                        in_string = not in_string
                        continue
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            if brace_count == 1:
                                response_end = i + 1
                                break
                            brace_count -= 1
                
                response_str = parts_str[response_content_start:response_end]
                extracted_content = _extract_from_string_representation(response_str)
                
                return {
                    "type": "function_response",
                    "name": func_name,
                    "response": extracted_content
                }
        
        response_content = _extract_from_string_representation(parts_str)
        
        return {
            "type": "function_response",
            "name": func_name,
            "response": response_content
        }
    except Exception as e:
        return {
            "type": "function_response",
            "name": "unknown",
            "response": f"Error parsing response: {str(e)}"
        }
    
    return None


def _clean_response_data(response_data: Any) -> Any:
    """Clean up response data for better readability."""
    
    if isinstance(response_data, dict) and 'result' in response_data:
        result = response_data['result']
        return _extract_from_call_tool_result(result)
    
    if isinstance(response_data, str):
        if response_data.startswith("{'") and response_data.endswith("'}"):
            result = _extract_from_string_representation(response_data)
            return result
        elif 'CallToolResult(' in response_data:
            result = _extract_from_string_representation(response_data)
            return result
        else:
            return response_data
    
    if hasattr(response_data, '__dict__'):
        data_dict = response_data.__dict__
        
        if 'result' in data_dict:
            result = data_dict['result']
            return _extract_from_call_tool_result(result)
        
        if 'content' in data_dict:
            content = data_dict['content']
            if isinstance(content, list) and len(content) > 0:
                first_content = content[0]
                if hasattr(first_content, '__dict__') and 'text' in first_content.__dict__:
                    text_content = first_content.__dict__['text']
                    return _parse_json_or_return_text(text_content)
        
        return {k: str(v) for k, v in data_dict.items() if not k.startswith('_')}
    
    return str(response_data)


def _extract_from_call_tool_result(result: Any) -> Any:
    """Extract data from CallToolResult object."""
    if hasattr(result, '__dict__'):
        result_dict = result.__dict__
        
        if 'content' in result_dict and isinstance(result_dict['content'], list):
            content_list = result_dict['content']
            if len(content_list) > 0:
                first_content = content_list[0]
                if hasattr(first_content, '__dict__') and 'text' in first_content.__dict__:
                    text_content = first_content.__dict__['text']
                    return _parse_json_or_return_text(text_content)
        
        return {k: str(v) for k, v in result_dict.items() if not k.startswith('_') and v is not None}
    
    return str(result)


def _extract_from_string_representation(response_str: str) -> Any:
    """Extract JSON content from string representation of CallToolResult."""
    try:
        if 'TextContent(' in response_str and "text='" in response_str:
            text_pattern = "text='"
            text_start = response_str.find(text_pattern)
            
            if text_start > -1:
                content_start = text_start + len(text_pattern)
                
                end_pattern = "', annotations"
                content_end = response_str.find(end_pattern, content_start)
                
                if content_end > content_start:
                    raw_content = response_str[content_start:content_end]
                    
                    clean_content = raw_content.replace('\\n', '\n')
                    clean_content = clean_content.replace('\\"', '"')
                    clean_content = clean_content.replace("\\'", "'")
                    clean_content = clean_content.replace('\\\\', '\\')
                    
                    return _parse_json_or_return_text(clean_content)
        
        if "'result':" in response_str and 'CallToolResult(' in response_str:
            start_brace = response_str.find('{')
            if start_brace > -1:
                brace_count = 0
                end_pos = start_brace
                
                for i in range(start_brace, len(response_str)):
                    char = response_str[i]
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break
                
                if end_pos > start_brace:
                    dict_content = response_str[start_brace:end_pos]
                    return _extract_nested_result(dict_content)
        
        json_start = response_str.find('{')
        if json_start > -1:
            brace_count = 0
            json_end = json_start
            in_string = False
            escape_next = False
            
            for i in range(json_start, len(response_str)):
                char = response_str[i]
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
            
            if json_end > json_start:
                json_content = response_str[json_start:json_end]
                json_content = json_content.replace('\\n', '\n').replace('\\"', '"')
                return _parse_json_or_return_text(json_content)
    
    except Exception as e:
        return f"Error extracting content: {str(e)}"
    
    return "Could not extract response content"


def _extract_nested_result(dict_str: str) -> Any:
    """Extract nested result content from CallToolResult dictionary string."""
    try:
        if "text='" in dict_str:
            text_start = dict_str.find("text='") + 6
            text_end = text_start
            escape_next = False
            
            while text_end < len(dict_str):
                char = dict_str[text_end]
                if escape_next:
                    escape_next = False
                    text_end += 1
                    continue
                if char == '\\':
                    escape_next = True
                    text_end += 1
                    continue
                if char == "'" and not escape_next:
                    if text_end + 1 < len(dict_str) and dict_str[text_end + 1] in ',)':
                        break
                text_end += 1
            
            if text_end > text_start:
                raw_text = dict_str[text_start:text_end]
                clean_text = raw_text.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
                return _parse_json_or_return_text(clean_text)
    except Exception:
        pass
    
    return dict_str


def _parse_json_or_return_text(text_content: str) -> Any:
    """Try to parse text as JSON, return as text if it fails."""
    if not text_content:
        return "Empty response"
    
    text_content = text_content.strip()
    
    if text_content.startswith(('{', '[')):
        try:
            return json.loads(text_content)
        except json.JSONDecodeError:
            pass
    
    return text_content
