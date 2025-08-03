from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class AIAgent(db.Model):
    __tablename__ = "ai_agents"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    twitter_handle = db.Column(db.String(50), unique=True)
    twitter_api_key = db.Column(db.String(255))
    twitter_api_secret = db.Column(db.String(255))
    twitter_access_token = db.Column(db.String(255))
    twitter_access_token_secret = db.Column(db.String(255))
    authority_level = db.Column(
        db.String(20), default="Limited"
    )  # None, Limited, Moderate, Full
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime)

    # Relationships
    boardroom_sessions = db.relationship("BoardroomSession", backref="agent", lazy=True)
    votes = db.relationship("Vote", backref="agent", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "twitter_handle": self.twitter_handle,
            "authority_level": self.authority_level,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
        }


class BoardroomSession(db.Model):
    __tablename__ = "boardroom_sessions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    session_type = db.Column(
        db.String(50), default="debate"
    )  # debate, vote, discussion
    status = db.Column(
        db.String(20), default="scheduled"
    )  # scheduled, active, completed, cancelled
    x_space_id = db.Column(db.String(100))  # X Spaces ID
    x_space_url = db.Column(db.String(255))  # X Spaces URL
    scheduled_start = db.Column(db.DateTime, nullable=False)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    moderator_agent_id = db.Column(db.Integer, db.ForeignKey("ai_agents.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    participants = db.relationship("SessionParticipant", backref="session", lazy=True)
    agenda_items = db.relationship("AgendaItem", backref="session", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "session_type": self.session_type,
            "status": self.status,
            "x_space_id": self.x_space_id,
            "x_space_url": self.x_space_url,
            "scheduled_start": (
                self.scheduled_start.isoformat() if self.scheduled_start else None
            ),
            "actual_start": (
                self.actual_start.isoformat() if self.actual_start else None
            ),
            "actual_end": self.actual_end.isoformat() if self.actual_end else None,
            "moderator_agent_id": self.moderator_agent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SessionParticipant(db.Model):
    __tablename__ = "session_participants"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("boardroom_sessions.id"), nullable=False
    )
    agent_id = db.Column(db.Integer, db.ForeignKey("ai_agents.id"), nullable=False)
    role = db.Column(
        db.String(20), default="participant"
    )  # moderator, speaker, participant, observer
    joined_at = db.Column(db.DateTime)
    left_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "role": self.role,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "left_at": self.left_at.isoformat() if self.left_at else None,
        }


class AgendaItem(db.Model):
    __tablename__ = "agenda_items"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("boardroom_sessions.id"), nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    item_type = db.Column(
        db.String(50), default="discussion"
    )  # discussion, vote, announcement
    order_index = db.Column(db.Integer, default=0)
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, active, completed, skipped
    duration_minutes = db.Column(db.Integer, default=10)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Relationships
    votes = db.relationship("Vote", backref="agenda_item", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "title": self.title,
            "description": self.description,
            "item_type": self.item_type,
            "order_index": self.order_index,
            "status": self.status,
            "duration_minutes": self.duration_minutes,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


class Vote(db.Model):
    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True)
    agenda_item_id = db.Column(
        db.Integer, db.ForeignKey("agenda_items.id"), nullable=False
    )
    agent_id = db.Column(db.Integer, db.ForeignKey("ai_agents.id"), nullable=False)
    vote_value = db.Column(db.String(20), nullable=False)  # yes, no, abstain
    reasoning = db.Column(db.Text)  # AI agent's reasoning for the vote
    confidence_score = db.Column(db.Float)  # 0.0 to 1.0
    cast_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "agenda_item_id": self.agenda_item_id,
            "agent_id": self.agent_id,
            "vote_value": self.vote_value,
            "reasoning": self.reasoning,
            "confidence_score": self.confidence_score,
            "cast_at": self.cast_at.isoformat() if self.cast_at else None,
        }


class BoardroomMessage(db.Model):
    __tablename__ = "boardroom_messages"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("boardroom_sessions.id"), nullable=False
    )
    agent_id = db.Column(db.Integer, db.ForeignKey("ai_agents.id"), nullable=False)
    message_type = db.Column(
        db.String(20), default="speech"
    )  # speech, announcement, vote_call
    content = db.Column(db.Text, nullable=False)
    audio_file_path = db.Column(db.String(255))  # Path to generated TTS audio
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    x_posted = db.Column(db.Boolean, default=False)  # Whether posted to X/Twitter

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "message_type": self.message_type,
            "content": self.content,
            "audio_file_path": self.audio_file_path,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "x_posted": self.x_posted,
        }
