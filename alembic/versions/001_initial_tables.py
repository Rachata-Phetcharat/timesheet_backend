"""create initial tables

Revision ID: 001_initial_tables
Revises: 
Create Date: 2026-08-25 22:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Employees table
    op.create_table(
        'employees',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('staff', 'admin', name='employee_role'), nullable=False, server_default='staff'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employees_email'), 'employees', ['email'], unique=True)

    # Attendance records table
    op.create_table(
        'attendance_records',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('employee_id', sa.String(), nullable=False),
        sa.Column('clock_in_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clock_out_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('on_time', 'late', 'absent', name='attendance_status'), nullable=False),
        sa.Column('late_minutes', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attendance_records_employee_id'), 'attendance_records', ['employee_id'], unique=False)

    # Leave requests table
    op.create_table(
        'leave_requests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('employee_id', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('personal', 'sick', name='leave_type'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='leave_status'), nullable=False, server_default='pending'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_requests_employee_id'), 'leave_requests', ['employee_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_leave_requests_employee_id'), table_name='leave_requests')
    op.drop_table('leave_requests')
    op.execute("DROP TYPE IF EXISTS leave_status")
    op.execute("DROP TYPE IF EXISTS leave_type")

    op.drop_index(op.f('ix_attendance_records_employee_id'), table_name='attendance_records')
    op.drop_table('attendance_records')
    op.execute("DROP TYPE IF EXISTS attendance_status")

    op.drop_index(op.f('ix_employees_email'), table_name='employees')
    op.drop_table('employees')
    op.execute("DROP TYPE IF EXISTS employee_role")
