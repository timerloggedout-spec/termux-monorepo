"""
Resilient message field adapter.
Detects which field names the API returned and normalizes to what build_tree_str expects.
"""
def detect_field_mapping(sample_message):
    """Given a single message dict, return a mapping from canonical -> actual field names."""
    canonical_actual = {}
    # message_id could be: message_id, id, msg_id
    for key in ['message_id', 'id', 'msg_id']:
        if key in sample_message:
            canonical_actual['message_id'] = key
            break
    # parent_id could be: parent_id, parent, parent_message_id
    for key in ['parent_id', 'parent', 'parent_message_id']:
        if key in sample_message:
            canonical_actual['parent_id'] = key
            break
    # content could be: content, text, body
    for key in ['content', 'text', 'body']:
        if key in sample_message:
            canonical_actual['content'] = key
            break
    # role could be: role, author, type
    for key in ['role', 'author', 'type']:
        if key in sample_message:
            canonical_actual['role'] = key
            break
    return canonical_actual

def normalize_messages(messages):
    """Given a list of message dicts, return a new list with canonical field names."""
    if not messages:
        return []
    mapping = detect_field_mapping(messages[0])
    normalized = []
    for msg in messages:
        norm = {}
        # Copy all original fields
        norm.update(msg)
        # Add canonical field names pointing to the actual values
        for canon, actual in mapping.items():
            if actual in msg:
                norm[canon] = msg[actual]
        normalized.append(norm)
    return normalized
