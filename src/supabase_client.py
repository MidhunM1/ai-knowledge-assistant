
from supabase import create_client

from config import SUPABASE_URL, SUPABASE_KEY


def get_supabase_client(access_token=None, refresh_token=None):

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase URL or key is missing. "
            "Check your .env file."
        )

    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    if access_token and refresh_token:
        supabase.auth.set_session(
            access_token,
            refresh_token
        )

    return supabase
