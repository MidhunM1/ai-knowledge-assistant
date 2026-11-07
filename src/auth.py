
from src.supabase_client import get_supabase_client


def sign_up(email, password, display_name):
    supabase = get_supabase_client()

    response = supabase.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "display_name": display_name
            }
        }
    })

    return response


def sign_in(email, password):
    supabase = get_supabase_client()

    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    return response


def sign_out(access_token, refresh_token):
    supabase = get_supabase_client(
        access_token,
        refresh_token
    )

    supabase.auth.sign_out()
