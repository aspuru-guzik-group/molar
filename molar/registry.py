from typing import Any, Dict, List, Optional, Union

REGISTRIES: Dict[str, Any] = {
    "mappers": [],
    "queries": [],
    "sql": [],
    "alembic_revision": {},
}


def register_mapper(
    name: str,
    table: str,
    requirements: Optional[List[Dict[str, str]]] = None,
    requirements_bonus: int = 0,
):
    def register_mapper_inner(func):
        REGISTRIES["mappers"].append(
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
    name: str,
    table: str,
    requirements: Optional[List[Dict[str, str]]],
    requirements_bonus: int = 0,
):
    def register_query_inner(func):
        REGISTRIES["queries"].append(
            {
                "name": name,
                "table": table,
                "func": func,
                "requirements": requirements,
                "requirement_bonus": requirements_bonus,
            }
        )
        return func

    return register_query_inner


def register_sql(
    name: str,
    table: str,
    requirements: Optional[List[Dict[str, str]]],
    requirements_bonus: int = 0,
):
    def register_sql_inner(func):
        REGISTRIES["sql"].append(
            {
                "name": name,
                "func": func,
                "table": table,
                "requirements": requirements,
                "requirements_bonus": requirements_bonus,
            }
        )
        return func

    return register_sql_inner


def compute_requirement_score(
    database_structure: Dict[str, List[str]],
    requirements: Optional[List[Dict[str, str]]],
    requirements_bonus: int,
) -> int:
    score = requirements_bonus

    if requirements is None:
        return score

    for req in requirements:
        if req["name"] in database_structure[req["type"]]:
            score += 1

    return score


def register_alembic_branch(
    branch_label: str,
    options: List[Dict[str, Union[str, bool]]],
    help: str,
    default: bool,
):
    if branch_label in REGISTRIES["alembic_revision"].keys():
        raise ValueError(
            (
                f"alembic branch {branch_label} could not be registered: "
                f" there is already a revision with the same name."
            )
        )

    REGISTRIES["alembic_revision"][branch_label] = {
        "options": options,
        "help": help,
        "default": default,
    }
