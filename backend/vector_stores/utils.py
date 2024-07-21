import tiktoken


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns number of tokens given an openai model"""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
