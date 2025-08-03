from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.agent import db, AIAgent, BoardroomSession, BoardroomMessage
from src.services.x_api_service import XAPIService
import json

x_integration_bp = Blueprint("x_integration", __name__)
x_api_service = XAPIService()


@x_integration_bp.route("/validate-credentials/<int:agent_id>", methods=["POST"])
def validate_agent_credentials(agent_id):
    """Validate X API credentials for an agent"""
    agent = AIAgent.query.get_or_404(agent_id)

    credentials = x_api_service.get_agent_credentials(agent_id)

    if not all(credentials.values()):
        return (
            jsonify({"success": False, "error": "Missing API credentials for agent"}),
            400,
        )

    result = x_api_service.validate_credentials(credentials)

    if result["success"]:
        # Update agent's last activity
        agent.last_activity = datetime.utcnow()
        db.session.commit()

    return jsonify(result)


@x_integration_bp.route("/create-space", methods=["POST"])
def create_space():
    """Create a new X Space for a boardroom session"""
    data = request.get_json()

    session_id = data.get("session_id")
    moderator_agent_id = data.get("moderator_agent_id")

    if not session_id or not moderator_agent_id:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "session_id and moderator_agent_id are required",
                }
            ),
            400,
        )

    session = BoardroomSession.query.get_or_404(session_id)
    moderator = AIAgent.query.get_or_404(moderator_agent_id)

    # Get moderator's credentials
    credentials = x_api_service.get_agent_credentials(moderator_agent_id)

    if not all(credentials.values()):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Missing API credentials for moderator agent",
                }
            ),
            400,
        )

    # Create the Space
    space_result = x_api_service.create_space(
        credentials,
        session.title,
        session.description or f"DAO Boardroom Session: {session.title}",
    )

    if space_result["success"]:
        # Update session with Space information
        session.x_space_id = space_result["space_id"]
        session.x_space_url = space_result["space_url"]
        session.status = "active"
        session.actual_start = datetime.utcnow()

        db.session.commit()

        # Post announcement tweet
        announcement_text = f"🚀 DAO Boardroom Session '{session.title}' is now LIVE! Join us in X Spaces for transparent governance discussions. #DAO #Governance #AI"

        tweet_result = x_api_service.post_tweet(
            credentials, announcement_text, space_result["space_id"]
        )

        return jsonify(
            {
                "success": True,
                "space_id": space_result["space_id"],
                "space_url": space_result["space_url"],
                "session_id": session_id,
                "tweet_posted": tweet_result.get("success", False),
            }
        )
    else:
        return jsonify(space_result), 400


@x_integration_bp.route("/end-space", methods=["POST"])
def end_space():
    """End an active X Space"""
    data = request.get_json()

    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"success": False, "error": "session_id is required"}), 400

    session = BoardroomSession.query.get_or_404(session_id)

    if not session.x_space_id:
        return (
            jsonify(
                {"success": False, "error": "No active Space found for this session"}
            ),
            400,
        )

    # Get moderator's credentials
    moderator = AIAgent.query.get_or_404(session.moderator_agent_id)
    credentials = x_api_service.get_agent_credentials(session.moderator_agent_id)

    if not all(credentials.values()):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Missing API credentials for moderator agent",
                }
            ),
            400,
        )

    # End the Space
    end_result = x_api_service.end_space(credentials, session.x_space_id)

    if end_result["success"]:
        # Update session status
        session.status = "completed"
        session.actual_end = datetime.utcnow()

        db.session.commit()

        # Post summary tweet
        summary_text = f"✅ DAO Boardroom Session '{session.title}' has concluded. Thank you to all participants for transparent governance! #DAO #Governance #AI"

        tweet_result = x_api_service.post_tweet(credentials, summary_text)

        return jsonify(
            {
                "success": True,
                "session_id": session_id,
                "ended_at": end_result["ended_at"],
                "summary_tweet_posted": tweet_result.get("success", False),
            }
        )
    else:
        return jsonify(end_result), 400


@x_integration_bp.route("/post-message", methods=["POST"])
def post_message_to_x():
    """Post a boardroom message to X/Twitter"""
    data = request.get_json()

    message_id = data.get("message_id")

    if not message_id:
        return jsonify({"success": False, "error": "message_id is required"}), 400

    message = BoardroomMessage.query.get_or_404(message_id)
    agent = AIAgent.query.get_or_404(message.agent_id)
    session = BoardroomSession.query.get_or_404(message.session_id)

    # Get agent's credentials
    credentials = x_api_service.get_agent_credentials(message.agent_id)

    if not all(credentials.values()):
        return (
            jsonify({"success": False, "error": "Missing API credentials for agent"}),
            400,
        )

    # Format the tweet content
    tweet_content = f"🤖 {agent.name}: {message.content}"

    # Add session context if available
    if session.x_space_id:
        tweet_content += f"\n\n🎙️ Live in DAO Boardroom: {session.title}"

    # Truncate if too long (X has character limits)
    if len(tweet_content) > 280:
        tweet_content = tweet_content[:277] + "..."

    # Post the tweet
    tweet_result = x_api_service.post_tweet(
        credentials, tweet_content, session.x_space_id if session.x_space_id else None
    )

    if tweet_result["success"]:
        # Mark message as posted to X
        message.x_posted = True
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "tweet_id": tweet_result["tweet_id"],
                "message_id": message_id,
                "posted_at": tweet_result["posted_at"],
            }
        )
    else:
        return jsonify(tweet_result), 400


@x_integration_bp.route("/space-info/<space_id>", methods=["GET"])
def get_space_info(space_id):
    """Get information about a specific X Space"""
    # Find the session associated with this Space
    session = BoardroomSession.query.filter_by(x_space_id=space_id).first()

    if not session:
        return (
            jsonify({"success": False, "error": "No session found for this Space ID"}),
            404,
        )

    # Get moderator's credentials
    credentials = x_api_service.get_agent_credentials(session.moderator_agent_id)

    if not all(credentials.values()):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Missing API credentials for moderator agent",
                }
            ),
            400,
        )

    # Get Space information
    space_info = x_api_service.get_space_info(credentials, space_id)

    if space_info["success"]:
        # Add session context
        space_info["session_info"] = {
            "session_id": session.id,
            "title": session.title,
            "description": session.description,
            "status": session.status,
            "scheduled_start": (
                session.scheduled_start.isoformat() if session.scheduled_start else None
            ),
            "actual_start": (
                session.actual_start.isoformat() if session.actual_start else None
            ),
            "actual_end": (
                session.actual_end.isoformat() if session.actual_end else None
            ),
        }

    return jsonify(space_info)


@x_integration_bp.route("/agent-tweet", methods=["POST"])
def post_agent_tweet():
    """Post a tweet from a specific AI agent"""
    data = request.get_json()

    agent_id = data.get("agent_id")
    content = data.get("content")
    session_id = data.get("session_id")  # Optional

    if not agent_id or not content:
        return (
            jsonify({"success": False, "error": "agent_id and content are required"}),
            400,
        )

    agent = AIAgent.query.get_or_404(agent_id)

    # Get agent's credentials
    credentials = x_api_service.get_agent_credentials(agent_id)

    if not all(credentials.values()):
        return (
            jsonify({"success": False, "error": "Missing API credentials for agent"}),
            400,
        )

    # Get Space ID if session is provided
    space_id = None
    if session_id:
        session = BoardroomSession.query.get(session_id)
        if session:
            space_id = session.x_space_id

    # Post the tweet
    tweet_result = x_api_service.post_tweet(credentials, content, space_id)

    if tweet_result["success"]:
        # Create a message record if this is part of a session
        if session_id:
            message = BoardroomMessage(
                session_id=session_id,
                agent_id=agent_id,
                message_type="announcement",
                content=content,
                x_posted=True,
            )
            db.session.add(message)
            db.session.commit()

        # Update agent's last activity
        agent.last_activity = datetime.utcnow()
        db.session.commit()

    return jsonify(tweet_result)


@x_integration_bp.route("/search-spaces", methods=["GET"])
def search_spaces():
    """Search for X Spaces"""
    query = request.args.get("query", "")
    max_results = request.args.get("max_results", 10, type=int)

    if not query:
        return jsonify({"success": False, "error": "query parameter is required"}), 400

    search_result = x_api_service.search_spaces(query, max_results)

    return jsonify(search_result)


@x_integration_bp.route("/agents-status", methods=["GET"])
def get_agents_x_status():
    """Get X API status for all agents"""
    agents = AIAgent.query.filter_by(active=True).all()

    agent_statuses = []

    for agent in agents:
        credentials = x_api_service.get_agent_credentials(agent.id)

        if all(credentials.values()):
            validation_result = x_api_service.validate_credentials(credentials)
            status = {
                "agent_id": agent.id,
                "agent_name": agent.name,
                "twitter_handle": agent.twitter_handle,
                "credentials_valid": validation_result.get("success", False),
                "x_user_id": validation_result.get("user_id"),
                "x_username": validation_result.get("username"),
            }
        else:
            status = {
                "agent_id": agent.id,
                "agent_name": agent.name,
                "twitter_handle": agent.twitter_handle,
                "credentials_valid": False,
                "error": "Missing API credentials",
            }

        agent_statuses.append(status)

    return jsonify(
        {
            "success": True,
            "agents": agent_statuses,
            "total_agents": len(agent_statuses),
            "valid_credentials": sum(
                1 for status in agent_statuses if status.get("credentials_valid", False)
            ),
        }
    )
