from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.agent import (
    db,
    AIAgent,
    BoardroomSession,
    SessionParticipant,
    AgendaItem,
    Vote,
    BoardroomMessage,
)
import json

boardroom_bp = Blueprint("boardroom", __name__)


@boardroom_bp.route("/agents", methods=["GET"])
def get_agents():
    """Get all AI agents"""
    agents = AIAgent.query.filter_by(active=True).all()
    return jsonify([agent.to_dict() for agent in agents])


@boardroom_bp.route("/agents", methods=["POST"])
def create_agent():
    """Create a new AI agent"""
    data = request.get_json()

    agent = AIAgent(
        name=data.get("name"),
        description=data.get("description"),
        twitter_handle=data.get("twitter_handle"),
        authority_level=data.get("authority_level", "Limited"),
    )

    db.session.add(agent)
    db.session.commit()

    return jsonify(agent.to_dict()), 201


@boardroom_bp.route("/agents/<int:agent_id>", methods=["PUT"])
def update_agent(agent_id):
    """Update an AI agent"""
    agent = AIAgent.query.get_or_404(agent_id)
    data = request.get_json()

    agent.name = data.get("name", agent.name)
    agent.description = data.get("description", agent.description)
    agent.twitter_handle = data.get("twitter_handle", agent.twitter_handle)
    agent.authority_level = data.get("authority_level", agent.authority_level)
    agent.active = data.get("active", agent.active)

    db.session.commit()

    return jsonify(agent.to_dict())


@boardroom_bp.route("/sessions", methods=["GET"])
def get_sessions():
    """Get all boardroom sessions"""
    sessions = BoardroomSession.query.order_by(
        BoardroomSession.scheduled_start.desc()
    ).all()
    return jsonify([session.to_dict() for session in sessions])


@boardroom_bp.route("/sessions", methods=["POST"])
def create_session():
    """Create a new boardroom session"""
    data = request.get_json()

    session = BoardroomSession(
        title=data.get("title"),
        description=data.get("description"),
        session_type=data.get("session_type", "debate"),
        scheduled_start=datetime.fromisoformat(data.get("scheduled_start")),
        moderator_agent_id=data.get("moderator_agent_id"),
    )

    db.session.add(session)
    db.session.commit()

    # Add participants
    participant_ids = data.get("participant_ids", [])
    for agent_id in participant_ids:
        participant = SessionParticipant(
            session_id=session.id, agent_id=agent_id, role="participant"
        )
        db.session.add(participant)

    # Add moderator as participant
    if session.moderator_agent_id:
        moderator_participant = SessionParticipant(
            session_id=session.id, agent_id=session.moderator_agent_id, role="moderator"
        )
        db.session.add(moderator_participant)

    db.session.commit()

    return jsonify(session.to_dict()), 201


@boardroom_bp.route("/sessions/<int:session_id>", methods=["GET"])
def get_session(session_id):
    """Get a specific boardroom session with details"""
    session = BoardroomSession.query.get_or_404(session_id)

    # Get participants
    participants = (
        db.session.query(SessionParticipant, AIAgent)
        .join(AIAgent, SessionParticipant.agent_id == AIAgent.id)
        .filter(SessionParticipant.session_id == session_id)
        .all()
    )

    # Get agenda items
    agenda_items = (
        AgendaItem.query.filter_by(session_id=session_id)
        .order_by(AgendaItem.order_index)
        .all()
    )

    session_data = session.to_dict()
    session_data["participants"] = [
        {"participant": participant.to_dict(), "agent": agent.to_dict()}
        for participant, agent in participants
    ]
    session_data["agenda_items"] = [item.to_dict() for item in agenda_items]

    return jsonify(session_data)


@boardroom_bp.route("/sessions/<int:session_id>/start", methods=["POST"])
def start_session(session_id):
    """Start a boardroom session"""
    session = BoardroomSession.query.get_or_404(session_id)

    if session.status != "scheduled":
        return jsonify({"error": "Session is not in scheduled state"}), 400

    session.status = "active"
    session.actual_start = datetime.utcnow()

    # TODO: Create X Space here
    # session.x_space_id = create_x_space(session.title, session.description)

    db.session.commit()

    return jsonify(session.to_dict())


@boardroom_bp.route("/sessions/<int:session_id>/end", methods=["POST"])
def end_session(session_id):
    """End a boardroom session"""
    session = BoardroomSession.query.get_or_404(session_id)

    if session.status != "active":
        return jsonify({"error": "Session is not active"}), 400

    session.status = "completed"
    session.actual_end = datetime.utcnow()

    # TODO: End X Space here

    db.session.commit()

    return jsonify(session.to_dict())


@boardroom_bp.route("/sessions/<int:session_id>/agenda", methods=["POST"])
def add_agenda_item(session_id):
    """Add an agenda item to a session"""
    session = BoardroomSession.query.get_or_404(session_id)
    data = request.get_json()

    # Get the next order index
    max_order = (
        db.session.query(db.func.max(AgendaItem.order_index))
        .filter_by(session_id=session_id)
        .scalar()
        or 0
    )

    agenda_item = AgendaItem(
        session_id=session_id,
        title=data.get("title"),
        description=data.get("description"),
        item_type=data.get("item_type", "discussion"),
        order_index=max_order + 1,
        duration_minutes=data.get("duration_minutes", 10),
    )

    db.session.add(agenda_item)
    db.session.commit()

    return jsonify(agenda_item.to_dict()), 201


@boardroom_bp.route("/agenda/<int:item_id>/vote", methods=["POST"])
def cast_vote(item_id):
    """Cast a vote on an agenda item"""
    agenda_item = AgendaItem.query.get_or_404(item_id)
    data = request.get_json()

    # Check if agent already voted
    existing_vote = Vote.query.filter_by(
        agenda_item_id=item_id, agent_id=data.get("agent_id")
    ).first()

    if existing_vote:
        return jsonify({"error": "Agent has already voted on this item"}), 400

    vote = Vote(
        agenda_item_id=item_id,
        agent_id=data.get("agent_id"),
        vote_value=data.get("vote_value"),
        reasoning=data.get("reasoning"),
        confidence_score=data.get("confidence_score"),
    )

    db.session.add(vote)
    db.session.commit()

    return jsonify(vote.to_dict()), 201


@boardroom_bp.route("/agenda/<int:item_id>/votes", methods=["GET"])
def get_votes(item_id):
    """Get all votes for an agenda item"""
    votes = (
        db.session.query(Vote, AIAgent)
        .join(AIAgent, Vote.agent_id == AIAgent.id)
        .filter(Vote.agenda_item_id == item_id)
        .all()
    )

    return jsonify(
        [{"vote": vote.to_dict(), "agent": agent.to_dict()} for vote, agent in votes]
    )


@boardroom_bp.route("/sessions/<int:session_id>/messages", methods=["POST"])
def add_message(session_id):
    """Add a message to a boardroom session"""
    session = BoardroomSession.query.get_or_404(session_id)
    data = request.get_json()

    message = BoardroomMessage(
        session_id=session_id,
        agent_id=data.get("agent_id"),
        message_type=data.get("message_type", "speech"),
        content=data.get("content"),
    )

    db.session.add(message)
    db.session.commit()

    # TODO: Generate TTS audio
    # TODO: Post to X/Twitter if required

    return jsonify(message.to_dict()), 201


@boardroom_bp.route("/sessions/<int:session_id>/messages", methods=["GET"])
def get_messages(session_id):
    """Get all messages for a session"""
    messages = (
        db.session.query(BoardroomMessage, AIAgent)
        .join(AIAgent, BoardroomMessage.agent_id == AIAgent.id)
        .filter(BoardroomMessage.session_id == session_id)
        .order_by(BoardroomMessage.timestamp)
        .all()
    )

    return jsonify(
        [
            {"message": message.to_dict(), "agent": agent.to_dict()}
            for message, agent in messages
        ]
    )


@boardroom_bp.route("/sessions/upcoming", methods=["GET"])
def get_upcoming_sessions():
    """Get upcoming boardroom sessions"""
    now = datetime.utcnow()
    sessions = (
        BoardroomSession.query.filter(
            BoardroomSession.scheduled_start > now,
            BoardroomSession.status == "scheduled",
        )
        .order_by(BoardroomSession.scheduled_start)
        .all()
    )

    return jsonify([session.to_dict() for session in sessions])


@boardroom_bp.route("/sessions/active", methods=["GET"])
def get_active_sessions():
    """Get currently active boardroom sessions"""
    sessions = BoardroomSession.query.filter_by(status="active").all()
    return jsonify([session.to_dict() for session in sessions])


@boardroom_bp.route("/stats", methods=["GET"])
def get_boardroom_stats():
    """Get boardroom statistics"""
    total_agents = AIAgent.query.filter_by(active=True).count()
    total_sessions = BoardroomSession.query.count()
    active_sessions = BoardroomSession.query.filter_by(status="active").count()
    completed_sessions = BoardroomSession.query.filter_by(status="completed").count()

    # Recent activity
    recent_sessions = BoardroomSession.query.filter(
        BoardroomSession.created_at > datetime.utcnow() - timedelta(days=7)
    ).count()

    return jsonify(
        {
            "total_agents": total_agents,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "recent_sessions": recent_sessions,
        }
    )
