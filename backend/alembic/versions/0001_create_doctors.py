"""create doctors table and seed clinical department roster

Revision ID: 0001_create_doctors
Revises:
Create Date: 2026-10-16
"""

from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision = "0001_create_doctors"
down_revision = None
branch_labels = None
depends_on = None

SEED_DOCTORS = [
    ("Dr. Rajesh Sharma", "CARDIOLOGY", "C-102"),
    ("Dr. Sunita Verma", "PEDIATRICS", "P-105"),
    ("Dr. Amit Patel", "ORTHOPEDICS", "O-201"),
    ("Dr. Shalini Sen", "DERMATOLOGY", "D-208"),
    ("Dr. Kabir Joshi", "NEUROLOGY", "N-305"),
    ("Dr. Neha Agarwal", "GENERAL", "G-101"),
]


def upgrade() -> None:
    doctors = op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("department", sa.String(length=40), nullable=False),
        sa.Column("room", sa.String(length=20), nullable=False, server_default=""),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_doctors_name"),
    )
    op.create_index("ix_doctors_department", "doctors", ["department"])

    now = datetime.now(UTC)
    op.bulk_insert(
        doctors,
        [
            {"name": name, "department": dept, "room": room, "active": True, "created_at": now}
            for name, dept, room in SEED_DOCTORS
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_doctors_department", table_name="doctors")
    op.drop_table("doctors")
