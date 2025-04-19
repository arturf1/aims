
from collections import defaultdict

def analyze_result_messages(messages):
    message_count = len(messages)

    messages_per_agent = defaultdict(int)
    messages_per_type = defaultdict(int)

    total_prompt_tokens = 0
    total_completion_tokens = 0

    tokens_per_agent = defaultdict(lambda: {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    })

    for msg in messages:
        # Source and type
        source = msg.get('source', 'unknown') if isinstance(msg, dict) else getattr(msg, 'source', 'unknown')
        msg_type = msg.get('type', 'unknown') if isinstance(msg, dict) else getattr(msg, 'type', 'unknown')
        usage = msg.get('models_usage', {}) if isinstance(msg, dict) else getattr(msg, 'models_usage', {})

        # Count messages
        messages_per_agent[source] += 1
        messages_per_type[msg_type] += 1

        # Token usage
        if usage:
            prompt = usage.get('prompt_tokens', 0) or 0 if isinstance(usage, dict) else getattr(usage, 'prompt_tokens', 0) or 0
            completion = usage.get('completion_tokens', 0) or 0 if isinstance(usage, dict) else getattr(usage, 'completion_tokens', 0) or 0

            total_prompt_tokens += prompt
            total_completion_tokens += completion

            tokens_per_agent[source]["prompt_tokens"] += prompt
            tokens_per_agent[source]["completion_tokens"] += completion
            tokens_per_agent[source]["total_tokens"] += (prompt + completion)

    return {
        "total_messages": message_count,
        "messages_per_agent": dict(messages_per_agent),
        "messages_per_type": dict(messages_per_type),
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_tokens": total_prompt_tokens + total_completion_tokens,
        "tokens_per_agent": dict(tokens_per_agent)
    } 
    
