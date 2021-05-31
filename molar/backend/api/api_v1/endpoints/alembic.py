# std
from typing import List, Optional

# external
from alembic import command
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

# molar
from molar.backend import alembic_utils, schemas
from molar.backend.api import deps

router = APIRouter()


@router.get("/revisions", response_model=List[schemas.Revision])
def get_alembic_revision():
    alembic_config = alembic_utils.get_alembic_config()
    revisions = alembic_utils.get_revisions(alembic_config)
    return [
        schemas.Revision(
            revision=r.revision, log_entry=r.log_entry, branch_labels=r.branch_labels
        )
        for r in revisions
    ]


@router.post("/upgrade")
def alembic_ugprade(
    database_name: str,
    revision: str,
    current_user=Depends(deps.get_current_active_superuser),
):
    alembic_config = alembic_utils.get_alembic_config(database_name)
    command.upgrade(alembic_config, revision)


@router.post("/downgrade")
def alembic_downgrade(
    database_name: str,
    revision: str,
    current_user=Depends(deps.get_current_active_superuser),
):
    alembic_config = alembic_utils.get_alembic_config(database_name)
    command.downgrade(alembic_config, revision)
