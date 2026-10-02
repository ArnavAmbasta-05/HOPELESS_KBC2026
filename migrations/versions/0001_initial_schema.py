"""Initial schema for KoreX Event Digital Twin

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. events
    op.create_table(
        'events',
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('timezone', sa.String(length=64), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('event_id')
    )

    # 2. venues
    op.create_table(
        'venues',
        sa.Column('venue_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('building', sa.String(length=100), nullable=False),
        sa.Column('venue_type', sa.String(length=32), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('venue_id')
    )
    op.create_index('ix_venues_event_id', 'venues', ['event_id'])
    op.create_index('ix_venues_event_id_building', 'venues', ['event_id', 'building'])

    # 3. sessions
    op.create_table(
        'sessions',
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('venue_id', sa.String(length=64), nullable=False),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('registrants', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['venue_id'], ['venues.venue_id']),
        sa.PrimaryKeyConstraint('session_id')
    )
    op.create_index('ix_sessions_event_id', 'sessions', ['event_id'])
    op.create_index('ix_sessions_venue_id', 'sessions', ['venue_id'])
    op.create_index('ix_sessions_event_id_date', 'sessions', ['event_id', 'session_date'])

    # 4. participants
    op.create_table(
        'participants',
        sa.Column('participant_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('arrival_building', sa.String(length=100), nullable=True),
        sa.Column('assigned_session_id', sa.String(length=64), nullable=True),
        sa.Column('assigned_venue_id', sa.String(length=64), nullable=True),
        sa.Column('skill', sa.String(length=64), nullable=True),
        sa.Column('volunteer_status', sa.String(length=32), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('participant_id')
    )
    op.create_index('ix_participants_event_id', 'participants', ['event_id'])
    op.create_index('ix_participants_event_role', 'participants', ['event_id', 'role'])

    # 5. resources
    op.create_table(
        'resources',
        sa.Column('resource_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=32), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('assigned_venue_id', sa.String(length=64), nullable=True),
        sa.Column('assigned_session_id', sa.String(length=64), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('resource_id')
    )
    op.create_index('ix_resources_event_id', 'resources', ['event_id'])

    # 6. vehicles & routes
    op.create_table(
        'vehicles',
        sa.Column('vehicle_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('current_location', sa.String(length=100), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('vehicle_id')
    )

    op.create_table(
        'routes',
        sa.Column('route_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('origin', sa.String(length=100), nullable=False),
        sa.Column('destination', sa.String(length=100), nullable=False),
        sa.Column('estimated_minutes', sa.Integer(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('route_id')
    )

    # 7. tasks
    op.create_table(
        'tasks',
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('team', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('venue_id', sa.String(length=64), nullable=True),
        sa.Column('session_id', sa.String(length=64), nullable=True),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('slack_minutes', sa.Integer(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('task_id')
    )

    # 8. notifications
    op.create_table(
        'notifications',
        sa.Column('notification_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('channel', sa.String(length=32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('mentions_venue_id', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('notification_id')
    )

    # 9. attendance_records
    op.create_table(
        'attendance_records',
        sa.Column('attendance_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('participant_id', sa.String(length=64), nullable=False),
        sa.Column('scanned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scanner_user_id', sa.String(length=64), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id']),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.participant_id']),
        sa.PrimaryKeyConstraint('attendance_id')
    )
    op.create_index('ix_attendance_event_session', 'attendance_records', ['event_id', 'session_id'])

    # 10. weather_signals
    op.create_table(
        'weather_signals',
        sa.Column('signal_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('forecast_window', sa.String(length=64), nullable=False),
        sa.Column('condition', sa.String(length=64), nullable=False),
        sa.Column('wind_speed_kmh', sa.Float(), nullable=False),
        sa.Column('rainfall_mm', sa.Float(), nullable=False),
        sa.Column('is_hazard', sa.Boolean(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('signal_id')
    )

    # 11. change_proposals
    op.create_table(
        'change_proposals',
        sa.Column('proposal_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('proposed_by', sa.String(length=64), nullable=False),
        sa.Column('approved_by', sa.String(length=64), nullable=True),
        sa.Column('plan_json', sa.JSON(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('proposal_id')
    )

    # 12. dependency_edges
    op.create_table(
        'dependency_edges',
        sa.Column('edge_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('source_id', sa.String(length=64), nullable=False),
        sa.Column('target_id', sa.String(length=64), nullable=False),
        sa.Column('edge_type', sa.String(length=32), nullable=False),
        sa.Column('validity_interval', sa.String(length=64), nullable=True),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('edge_id')
    )
    op.create_index('ix_edges_source_target_type', 'dependency_edges', ['event_id', 'source_id', 'target_id', 'edge_type'])

    # 13. incidents & escalations
    op.create_table(
        'incidents',
        sa.Column('incident_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('venue_id', sa.String(length=64), nullable=True),
        sa.Column('session_id', sa.String(length=64), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('incident_id')
    )

    op.create_table(
        'escalations',
        sa.Column('escalation_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=True),
        sa.Column('incident_id', sa.String(length=64), nullable=True),
        sa.Column('escalated_to_role', sa.String(length=64), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('escalation_id')
    )

    # 14. knowledge_items
    op.create_table(
        'knowledge_items',
        sa.Column('item_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('item_id')
    )

    # 15. audit_records (append-only)
    op.create_table(
        'audit_records',
        sa.Column('audit_id', sa.String(length=64), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('actor_id', sa.String(length=64), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.String(length=64), nullable=False),
        sa.Column('before_state', sa.JSON(), nullable=True),
        sa.Column('after_state', sa.JSON(), nullable=True),
        sa.Column('trace_id', sa.String(length=64), nullable=True),
        sa.Column('correlation_id', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('audit_id')
    )
    op.create_index('ix_audit_event_entity', 'audit_records', ['event_id', 'entity_type', 'entity_id'])


def downgrade() -> None:
    op.drop_table('audit_records')
    op.drop_table('knowledge_items')
    op.drop_table('escalations')
    op.drop_table('incidents')
    op.drop_table('dependency_edges')
    op.drop_table('change_proposals')
    op.drop_table('weather_signals')
    op.drop_table('attendance_records')
    op.drop_table('notifications')
    op.drop_table('tasks')
    op.drop_table('routes')
    op.drop_table('vehicles')
    op.drop_table('resources')
    op.drop_table('participants')
    op.drop_table('sessions')
    op.drop_table('venues')
    op.drop_table('events')
