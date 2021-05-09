"""empty message

Revision ID: 86283769a058
Revises: 
Create Date: 2021-05-05 17:13:21.947764

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86283769a058'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist_tokens',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('token', sa.String(length=500), nullable=False),
    sa.Column('blacklisted_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_table('oslist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('os_name', sa.String(length=30), nullable=False),
    sa.Column('aws_image_id', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('plan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_name', sa.String(length=30), nullable=False),
    sa.Column('aws_plan', sa.String(length=30), nullable=False),
    sa.Column('core', sa.Integer(), nullable=False),
    sa.Column('ram', sa.Integer(), nullable=False),
    sa.Column('traffic', sa.Integer(), nullable=False),
    sa.Column('ssd', sa.Integer(), nullable=False),
    sa.Column('iops', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('securitygroup_clouds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cloud_id', sa.Integer(), nullable=False),
    sa.Column('sec_group_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=60), nullable=False),
    sa.Column('_password', sa.Binary(), nullable=False),
    sa.Column('authenticated', sa.Boolean(), nullable=True),
    sa.Column('email_confirmation_sent_on', sa.DateTime(), nullable=True),
    sa.Column('email_confirmed', sa.Boolean(), nullable=True),
    sa.Column('email_confirmed_on', sa.DateTime(), nullable=True),
    sa.Column('registered_on', sa.DateTime(), nullable=True),
    sa.Column('last_logged_in', sa.DateTime(), nullable=True),
    sa.Column('current_logged_in', sa.DateTime(), nullable=True),
    sa.Column('role', sa.String(length=60), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('balance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('credit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('deposit_name', sa.Integer(), nullable=True),
    sa.Column('bank', sa.String(length=12), nullable=False),
    sa.Column('charge_amount', sa.Integer(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoice',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('payment_amount', sa.Integer(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=25), nullable=False),
    sa.Column('notes', sa.String(length=25), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('keypair',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('fingerprint', sa.String(length=59), nullable=True),
    sa.Column('keyid', sa.String(length=30), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('keytoken', sa.String(length=60), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('support',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('support_type', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id', 'title')
    )
    op.create_table('user_vpc',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('vpc_id', sa.String(length=40), nullable=False),
    sa.Column('inter_gw_id', sa.String(length=40), nullable=False),
    sa.Column('default_subnet_id', sa.String(length=40), nullable=False),
    sa.Column('default_sec_id', sa.String(length=40), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cloud',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hostname', sa.String(length=30), nullable=False),
    sa.Column('plan_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('os', sa.String(length=10), nullable=False),
    sa.Column('status', sa.String(length=15), nullable=False),
    sa.Column('ip_addr', sa.String(length=16), nullable=True),
    sa.Column('region', sa.String(length=10), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('keypair_id', sa.Integer(), nullable=True),
    sa.Column('vpc_id', sa.Integer(), nullable=True),
    sa.Column('aws_instance_id', sa.String(length=30), nullable=False),
    sa.ForeignKeyConstraint(['keypair_id'], ['keypair.id'], ),
    sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['vpc_id'], ['user_vpc.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reply_ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reply_to', sa.Integer(), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['reply_to'], ['support.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('securitygroup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('sec_group_id', sa.String(length=30), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('associated_to', sa.Integer(), nullable=True),
    sa.Column('vpc_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['vpc_id'], ['user_vpc.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subnets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subnet_id', sa.String(length=30), nullable=False),
    sa.Column('cidr_block_ipv4', sa.String(length=24), nullable=True),
    sa.Column('vpc_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['vpc_id'], ['user_vpc.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('netinterface',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('interface_id', sa.String(length=30), nullable=False),
    sa.Column('subnet_id', sa.Integer(), nullable=True),
    sa.Column('cloud_id', sa.Integer(), nullable=True),
    sa.Column('attached_at', sa.DateTime(), nullable=True),
    sa.Column('detached_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['subnet_id'], ['subnets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('securityrule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('protocol', sa.String(length=10), nullable=False),
    sa.Column('fromport', sa.Integer(), nullable=False),
    sa.Column('toport', sa.Integer(), nullable=False),
    sa.Column('cidr', sa.String(length=20), nullable=False),
    sa.Column('desc', sa.String(length=30), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['securitygroup.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('securityrule')
    op.drop_table('netinterface')
    op.drop_table('subnets')
    op.drop_table('securitygroup')
    op.drop_table('reply_ticket')
    op.drop_table('cloud')
    op.drop_table('user_vpc')
    op.drop_table('support')
    op.drop_table('keypair')
    op.drop_table('items')
    op.drop_table('invoice')
    op.drop_table('credit')
    op.drop_table('balance')
    op.drop_table('users')
    op.drop_table('securitygroup_clouds')
    op.drop_table('plan')
    op.drop_table('oslist')
    op.drop_table('blacklist_tokens')
    # ### end Alembic commands ###
