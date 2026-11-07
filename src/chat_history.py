from datetime import datetime, timezone

from src.supabase_client import get_supabase_client


def _client(access_token, refresh_token):
    """Return a Supabase client authenticated as the current user."""
    if not access_token or not refresh_token:
        raise ValueError("Your session has expired. Please log in again.")

    return get_supabase_client(access_token, refresh_token)


def create_conversation(access_token, refresh_token, user_id, title="New Chat"):
    """Create a conversation owned by the signed-in user."""
    supabase = _client(access_token, refresh_token)

    result = (
        supabase.table("conversations")
        .insert({
            "user_id": str(user_id),
            "title": title or "New Chat",
        })
        .select("*")
        .single()
        .execute()
    )
    return result.data


def get_conversations(access_token, refresh_token):
    """Return the signed-in user's conversations, newest first."""
    supabase = _client(access_token, refresh_token)

    result = (
        supabase.table("conversations")
        .select("*")
        .order("updated_at", desc=True)
        .execute()
    )
    return result.data or []


def get_messages(access_token, refresh_token, conversation_id):
    """Return messages for a conversation. RLS enforces ownership."""
    supabase = _client(access_token, refresh_token)

    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", str(conversation_id))
        .order("created_at")
        .execute()
    )
    return result.data or []


def save_message(
    access_token,
    refresh_token,
    conversation_id,
    role,
    content,
    model=None,
):
    """Save one user or assistant message and update conversation activity."""
    if role not in ("user", "assistant"):
        raise ValueError("Message role must be 'user' or 'assistant'.")

    if not content or not content.strip():
        raise ValueError("Message content cannot be empty.")

    supabase = _client(access_token, refresh_token)

    result = (
        supabase.table("messages")
        .insert({
            "conversation_id": str(conversation_id),
            "role": role,
            "content": content,
            "model": model,
        })
        .select("*")
        .single()
        .execute()
    )

    supabase.table("conversations").update({
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", str(conversation_id)).execute()

    return result.data


def rename_conversation(access_token, refresh_token, conversation_id, title):
    """Rename a conversation. RLS enforces ownership."""
    cleaned_title = (title or "").strip()
    if not cleaned_title:
        raise ValueError("Conversation title cannot be empty.")

    supabase = _client(access_token, refresh_token)

    result = (
        supabase.table("conversations")
        .update({
            "title": cleaned_title,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", str(conversation_id))
        .select("*")
        .single()
        .execute()
    )
    return result.data


def delete_conversation(access_token, refresh_token, conversation_id):
    """Delete a conversation. Its messages are removed by ON DELETE CASCADE."""
    supabase = _client(access_token, refresh_token)

    supabase.table("conversations").delete().eq(
        "id", str(conversation_id)
    ).execute()
