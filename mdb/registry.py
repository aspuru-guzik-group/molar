from typing import List

REGISTRIES = {"mappers": {}, "queries": {}, "sql": {}}


def register_mapper(name: str, tables: List[str] = None, functions: List[str] = None):
    def register_mapper_inner(func):
        if name in REGISTRIES["mapper"]:
            raise ValueError("Cannot register duplicate schema mapper")
        REGISTRIES["mapper"][name] = {
            "func": func,
            "tables": tables,
            "functions": functions,
        }
        return func

    return register_mapper_inner


def register_query(name: str, tables: List[str]):
    def register_query_inner(func):
        if name in REGISTRIES["query"]:
            raise ValueError("Cannot register duplicate query")
        REGISTRIES["query"][name] = {"func": func, "tables": tables}
        return func

    return register_query_inner


def register_sql(name: str):
    def register_sql_inner(func):
        if name in REGISTRIES["sql"]:
            raise ValueError("Cannot register duplicate sql query")
        REGISTRIES["sql"][name] = func
        return func

    return register_sql_inner
