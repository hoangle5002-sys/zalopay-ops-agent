"""
ZaloPay Merchant Support Chatbot
Flask application with 3 processing flows:
  1. Auto-answer from knowledge base
  2. Out-of-scope redirect to specialized department
  3. Escalate to human agent on sensitive situations
"""

import os
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from knowledge_base import (
    find_matching_domain,
    should_escalate,
    ESCALATION_RESPONSE,
    OUT_OF_SCOPE_RESPONSE,
)

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# In-memory conversation store (replace with Redis/DB in production)
# ─────────────────────────────────────────────────────────────────────────────

conversation_store: dict[str, list[dict]] = {}


# ─────────────────────────────────────────────────────────────────────────────
# Core processing logic
# ─────────────────────────────────────────────────────────────────────────────

class FlowType:
    AUTO_ANSWER = "auto_answer"
    OUT_OF_SCOPE = "out_of_scope"
    ESCALATED = "escalated"


def process_message(session_id: str, user_message: str) -> dict:
    """
    Routes an incoming merchant message through one of three flows:
      Flow A — Escalation: sensitive keywords or high negative sentiment detected
      Flow B — Knowledge base match: auto-answer from domain knowledge
      Flow C — Out of scope: politely redirect to specialist department
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    user_message_stripped = user_message.strip()

    if not user_message_stripped:
        return {
            "session_id": session_id,
            "flow": FlowType.AUTO_ANSWER,
            "response": "Kính gửi Quý đối tác, vui lòng nhập nội dung câu hỏi để được hỗ trợ.",
            "domain": None,
            "timestamp": timestamp,
            "escalated": False,
        }

    # ── Flow A: Escalation check (highest priority) ──────────────────────────
    if should_escalate(user_message_stripped):
        logger.warning(
            "ESCALATION triggered | session=%s | message_preview=%s",
            session_id,
            user_message_stripped[:80],
        )
        _store_turn(session_id, user_message_stripped, ESCALATION_RESPONSE, FlowType.ESCALATED)
        return {
            "session_id": session_id,
            "flow": FlowType.ESCALATED,
            "response": ESCALATION_RESPONSE,
            "domain": "escalation",
            "timestamp": timestamp,
            "escalated": True,
        }

    # ── Flow B: Knowledge base match ─────────────────────────────────────────
    matched_entry = find_matching_domain(user_message_stripped)
    if matched_entry:
        logger.info(
            "KB match | session=%s | domain=%s",
            session_id,
            matched_entry.domain,
        )
        response_text = matched_entry.response
        if matched_entry.follow_up:
            response_text += f"\n\n{matched_entry.follow_up}"

        _store_turn(session_id, user_message_stripped, response_text, FlowType.AUTO_ANSWER)
        return {
            "session_id": session_id,
            "flow": FlowType.AUTO_ANSWER,
            "response": response_text,
            "domain": matched_entry.domain,
            "timestamp": timestamp,
            "escalated": False,
        }

    # ── Flow C: Out of scope ──────────────────────────────────────────────────
    logger.info("Out-of-scope | session=%s", session_id)
    _store_turn(session_id, user_message_stripped, OUT_OF_SCOPE_RESPONSE, FlowType.OUT_OF_SCOPE)
    return {
        "session_id": session_id,
        "flow": FlowType.OUT_OF_SCOPE,
        "response": OUT_OF_SCOPE_RESPONSE,
        "domain": None,
        "timestamp": timestamp,
        "escalated": False,
    }


def _store_turn(session_id: str, user_msg: str, bot_msg: str, flow: str) -> None:
    if session_id not in conversation_store:
        conversation_store[session_id] = []
    conversation_store[session_id].append({
        "role": "user",
        "content": user_msg,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })
    conversation_store[session_id].append({
        "role": "assistant",
        "content": bot_msg,
        "flow": flow,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })


# ─────────────────────────────────────────────────────────────────────────────
# API routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/session", methods=["POST"])
def create_session():
    """Create a new chat session and return a session ID."""
    session_id = str(uuid.uuid4())
    conversation_store[session_id] = []
    logger.info("New session created: %s", session_id)
    return jsonify({"session_id": session_id})


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.
    Body: { "session_id": "...", "message": "..." }
    Returns: { "session_id", "flow", "response", "domain", "timestamp", "escalated" }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body phải là JSON hợp lệ."}), 400

    session_id = data.get("session_id", "").strip()
    message = data.get("message", "").strip()

    if not session_id:
        return jsonify({"error": "session_id là bắt buộc."}), 400
    if not message:
        return jsonify({"error": "message không được để trống."}), 400
    if len(message) > 2000:
        return jsonify({"error": "Tin nhắn vượt quá độ dài cho phép (2000 ký tự)."}), 400

    result = process_message(session_id, message)
    return jsonify(result)


@app.route("/api/history/<session_id>", methods=["GET"])
def get_history(session_id: str):
    """Return the full conversation history for a session."""
    history = conversation_store.get(session_id, [])
    return jsonify({"session_id": session_id, "history": history})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "zalopay-merchant-support"})


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
