"""empty message

Revision ID: f2339a0c16cb
Revises: 135045c56c28
Create Date: 2019-03-22 20:05:25.357253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2339a0c16cb'
down_revision = '135045c56c28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conciliaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_cuenta', sa.Integer(), nullable=True),
    sa.Column('fecha', sa.Date(), nullable=True),
    sa.Column('comentario', sa.String(length=250), nullable=True),
    sa.Column('ingreso_id', sa.Integer(), nullable=True),
    sa.Column('egreso_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('saldo_usuario', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('saldo_sistema', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['egreso_id'], ['egresos.id'], ),
    sa.ForeignKeyConstraint(['id_cuenta'], ['cuentas.id'], ),
    sa.ForeignKeyConstraint(['ingreso_id'], ['ingresos.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.add_column('cuentas', sa.Column('saldo_inicial', sa.Numeric(precision=10, scale=2), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cuentas', 'saldo_inicial')
    op.drop_table('conciliaciones')
    # ### end Alembic commands ###