from functools import lru_cache
import requests as rq

base_url = "http://commercial.duzzsystem.com.br:8080"


@lru_cache
def get_token(username: str, password: str, company: str):
    user_data = rq.get(
        base_url + "/auth/user",
        params={"username": username, "password": password, "company": company},
    )
    user_data.raise_for_status()
    user_data = user_data.json()

    return user_data["sessionToken"]


@lru_cache
def get_headers(company: str, session_token: str):
    return {"company": company, "sessionToken": session_token}
