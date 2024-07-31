import tiktoken


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns number of tokens given an openai model"""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def build_where_clause(filters):
    def format_condition(field, condition):
        parts = []
        for op, value in condition.items():
            if op == "gt":
                parts.append(f"{field} > '{value}'")
            elif op == "lt":
                parts.append(f"{field} < '{value}'")
            elif op == "eq":
                parts.append(f"{field} = '{value}'")
            elif op == "neq":
                parts.append(f"{field} != '{value}'")
            elif op == "in":
                format = [f"'{v}'" for v in value]
                parts.append(f"{field} IN ({', '.join(format)})")
            elif op == "iin":
                format = [f"'{v.lower()}'" for v in value]
                parts.append(f"LOWER({field}) IN ({', '.join(format)})")
            elif op == "like":
                parts.append(f"{field} LIKE '%{value}%'")
            elif op == "ilike":
                parts.append(f"LOWER({field}) LIKE '%{value.lower()}%'")
            else:
                raise ValueError(f"Unsupported operation: {op}")
        return " AND ".join(parts)

    def recurse(filters):
        if "AND" in filters:
            conditions = filters["AND"]
            and_parts = []
            for k, v in conditions.items():
                if isinstance(v, list):
                    and_parts.append(
                        "("
                        + " AND ".join(
                            [f"ARRAY_CONTAINS(c.{k}, '{item}')" for item in v]
                        )
                        + ")"
                    )
                else:
                    and_parts.append(recurse({k: v}))
            return "(" + " AND ".join(and_parts) + ")"
        elif "OR" in filters:
            conditions = filters["OR"]
            or_parts = []
            for k, v in conditions.items():
                if isinstance(v, list):
                    or_parts.append(
                        "("
                        + " OR ".join(
                            [f"ARRAY_CONTAINS(c.{k}, '{item}')" for item in v]
                        )
                        + ")"
                    )
                else:
                    or_parts.append(recurse({k: v}))
            return "(" + " OR ".join(or_parts) + ")"
        else:
            parts = []
            for field, condition in filters.items():
                if isinstance(condition, dict):
                    parts.append(format_condition(f"c.{field}", condition))
                elif isinstance(condition, list):
                    parts.append(
                        "("
                        + " OR ".join(
                            [f"ARRAY_CONTAINS(c.{field}, '{v}')" for v in condition]
                        )
                        + ")"
                    )
                else:
                    parts.append(f"c.{field} = '{condition}'")
            return " AND ".join(parts)

    applied_filters = recurse(filters)

    if applied_filters:
        return f"WHERE {applied_filters}"
    else:
        return ""
