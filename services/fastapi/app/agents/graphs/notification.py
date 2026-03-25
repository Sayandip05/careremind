"""
Notification Graph — LangGraph state machine for sending reminders.

Flow: load_context → check_optout → decrypt_phone → generate_message → try_whatsapp → try_sms

Replaces the old NotificationService.send_reminder() method.
"""

from langgraph.graph import END, StateGraph

from app.agents.state import NotificationState
from app.agents.nodes.notification import (
    load_context_node,
    check_optout_node,
    decrypt_phone_node,
    generate_message_node,
    try_whatsapp_node,
    try_sms_node,
)


def _should_continue_after_context(state: NotificationState) -> str:
    """Router: stop if context loading failed."""
    if state.get("status") == "error":
        return END
    return "check_optout"


def _should_continue_after_optout(state: NotificationState) -> str:
    """Router: stop if patient opted out."""
    if state.get("status") == "optout":
        return END
    return "decrypt_phone"


def _should_continue_after_decrypt(state: NotificationState) -> str:
    """Router: stop if phone decryption failed."""
    if state.get("status") == "error":
        return END
    return "generate_message"


def _should_try_sms_fallback(state: NotificationState) -> str:
    """Router: skip SMS if WhatsApp succeeded."""
    if state.get("status") == "sent":
        return END
    return "try_sms"


def build_notification_graph() -> StateGraph:
    """
    Build and compile the notification state graph.

    Graph:
        START → load_context → check_optout → decrypt_phone →
        generate_message → try_whatsapp → try_sms → END
    """
    graph = StateGraph(NotificationState)

    # ── Add nodes ────────────────────────────────────────────
    graph.add_node("load_context", load_context_node)
    graph.add_node("check_optout", check_optout_node)
    graph.add_node("decrypt_phone", decrypt_phone_node)
    graph.add_node("generate_message", generate_message_node)
    graph.add_node("try_whatsapp", try_whatsapp_node)
    graph.add_node("try_sms", try_sms_node)

    # ── Entry ────────────────────────────────────────────────
    graph.set_entry_point("load_context")

    # ── Conditional edges ────────────────────────────────────
    graph.add_conditional_edges("load_context", _should_continue_after_context)
    graph.add_conditional_edges("check_optout", _should_continue_after_optout)
    graph.add_conditional_edges("decrypt_phone", _should_continue_after_decrypt)
    graph.add_edge("generate_message", "try_whatsapp")
    graph.add_conditional_edges("try_whatsapp", _should_try_sms_fallback)
    graph.add_edge("try_sms", END)

    return graph.compile()


# Pre-built graph instance
notification_graph = build_notification_graph()
