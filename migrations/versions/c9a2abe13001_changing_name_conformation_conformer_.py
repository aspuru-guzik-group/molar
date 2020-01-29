"""Changing name Conformation -> Conformer and introducing better coordinates

Revision ID: c9a2abe13001
Revises: 10209c22a30e
Create Date: 2020-01-29 17:06:24.462619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9a2abe13001'
down_revision = '10209c22a30e'
branch_labels = None
depends_on = None


def upgrade():
    # Renaming
    op.execute('ALTER TABLE conformation RENAME TO conformer;') 
    op.execute('ALTER TABLE calculation RENAME COLUMN conformation_id TO conformer_id')
    op.execute('ALTER TABLE calculation RENAME COLUMN output_conformation TO output_conformer_id')

    # Conformer alteration
    op.execute('ALTER TABLE conformer DROP COLUMN coordinates;')
    op.execute('''ALTER TABLE conformer ADD COLUMN x FLOAT8[], 
                                      ADD COLUMN y FLOAT8[],
                                      ADD COLUMN z FLOAT8[],
                                      ADD COLUMN atomic_numbers INTEGER[];''')
    
    # calculation alteration
    op.execute('''ALTER TABLE calculation ADD COLUMN input TEXT,
                                          ADD COLUMN command_line TEXT;''')
    op.execute('''ALTER TABLE calculation
        RENAME CONSTRAINT lnk_conformation_calculation 
                       TO lnk_conformer_calculation,
        RENAME CONSTRAINT lnk_output_conformation_calculation 
                       TO lnk_output_conformer_calculation;''')
                


def downgrade():
    # Renaming
    op.execute('ALTER TABLE conformer RENAME TO conformation;')
    op.execute('''ALTER TABLE calculation 
        RENAME COLUMN conformer_id TO conformation_id ;''')
    op.execute('''ALTER TABLE calculation 
        RENAME COLUMN output_conformer_id TO output_conformation;''')
    
    # Conformer alteration
    op.execute('ALTER TABLE conformation ADD COLUMN coordinates jsonb;')
    op.execute('''ATLER TABLE conformation DROP COLUMN x,
                                           DROP COLUMN y,
                                           DROP COLUMN z,
                                           DROP COLUMN atomic_numbers;''')
    op.execute('''ALTER TABLE calculation
        RENAME CONSTRAINT lnk_conformer_calculation 
                       TO lnk_conformation_calculation,
        RENAME CONSTRAINT lnk_output_conformer_calculation 
                       TO lnk_output_conformation_calculation;''')
