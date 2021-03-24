from typing import List, Dict, Optional

REGISTRIES = {"mappers": [], "queries": [], "sql": []}


def register_mapper(
    name: str,
    table: str,
    requirements: Optional[List[Dict[str, str]]] = None,
    requirements_bonus: int = 0,
):
    def register_mapper_inner(func):
        REGISTRIES["mapper"].append(
            {
                "name": name,
                "table": table,
                "func": func,
                "requirements": requirements,
                "requirements_bonus": requirements_bonus,
            }
        )
        return func

    return register_mapper_inner


def register_query(
    name: str, requirements: Optional[List[Dict[str, str]]], requirements_bonus: int = 0
):
    def register_query_inner(func):
        REGISTRIES["query"].append(
            {
                "name": name,
                "func": func,
                "requirements": requirements,
                "requirement_bonus": requirements_bonus,
            }
        )
        return func

    return register_query_inner


def register_sql(
    name: str, requirements: Optional[List[Dict[str, str]]], requirements_bonus: int = 0
):
    def register_sql_inner(func):
        REGISTRIES["sql"].append(
            {
                "name": name,
                "func": func,
                "requirements": requirements,
                "requirements_bonus": requirements_bonus,
            }
        )
        return func

    return register_sql_inner
