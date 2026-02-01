"""Add_role_column_to_users

Revision ID: d0ee16694866
Revises: f220d9f8ff19
Create Date: 2026-02-01 ...

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql # 이 import가 필요합니다

# revision identifiers, used by Alembic.
revision = 'd0ee16694866'
down_revision = 'f220d9f8ff19'
branch_labels = None
depends_on = None

# Enum 정의
enum_type = postgresql.ENUM('USER', 'ADMIN', name='userrole')

def upgrade() -> None:

    # ENUM 타입 생성
    # 컬럼을 추가하기 전에 타입 생성
    enum_type.create(op.get_bind(), checkfirst=True)

    # 컬럼 추가
    op.add_column(
        'users',
        sa.Column('role', sa.Enum('USER', 'ADMIN', name='userrole'), nullable=False, server_default='USER')
    )


def downgrade() -> None:
    # 컬럼 삭제
    op.drop_column('users', 'role')

    # ENUM 타입 삭제
    enum_type.drop(op.get_bind(), checkfirst=True)