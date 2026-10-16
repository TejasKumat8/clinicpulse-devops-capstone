"""create appointments table with appointment_type support

Revision ID: 0002_create_appointments
Revises: 0001_create_doctors
Create Date: 2026-10-16
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_create_appointments"
down_revision = "0001_create_doctors"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_name", sa.String(length=120), nullable=False),
        sa.Column("patient_phone", sa.String(length=20), nullable=False),
        sa.Column(
            "doctor_id",
            sa.Integer(),
            sa.ForeignKey("doctors.id", name="fk_appointments_doctor_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("appointment_type", sa.String(length=20), nullable=False, server_default="IN_PERSON"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="SCHEDULED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("duration_minutes BETWEEN 10 AND 120", name="ck_appointments_duration"),
        sa.CheckConstraint(
            "status IN ('SCHEDULED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED', 'NO_SHOW')",
            name="ck_appointments_status",
        ),
        sa.CheckConstraint(
            "appointment_type IN ('IN_PERSON', 'TELECONSULT')",
            name="ck_appointments_type",
        ),
    )
    op.create_index("ix_appointments_patient_name", "appointments", ["patient_name"])
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_scheduled_at", "appointments", ["scheduled_at"])
    op.create_index("ix_appointments_status", "appointments", ["status"])
    op.create_index("ix_appointments_type", "appointments", ["appointment_type"])


def downgrade() -> None:
    op.drop_index("ix_appointments_type", table_name="appointments")
    op.drop_index("ix_appointments_status", table_name="appointments")
    op.drop_index("ix_appointments_scheduled_at", table_name="appointments")
    op.drop_index("ix_appointments_doctor_id", table_name="appointments")
    op.drop_index("ix_appointments_patient_name", table_name="appointments")
    op.drop_table("appointments")
