from psycopg2 import IntegrityError

from app.models.follow_model import add_follow, fetch_followers, fetch_following, is_following, remove_follow
from app.models.user_model import fetch_user_by_id


def _follow_row_to_dict(follow_row: tuple) -> dict:
    return {
        "id": follow_row[0],
        "follower_id": follow_row[1],
        "following_id": follow_row[2],
        "created_at": follow_row[3],
    }



def follow_user(follower_id: str, following_id: str) -> dict:
    follower_row = fetch_user_by_id(follower_id)
    if follower_row is None:
        raise ValueError("Follower user does not exist")

    following_row = fetch_user_by_id(following_id)
    if following_row is None:
        raise ValueError("Target user does not exist")

    if follower_id == following_id:
        raise ValueError("You cannot follow yourself")

    if is_following(follower_id, following_id):
        raise ValueError("Already following this user")

    try:
        add_follow(follower_id, following_id)
    except IntegrityError as exc:
        raise ValueError("Already following this user") from exc

    follows = fetch_following(follower_id)
    for follow_row in follows:
        if str(follow_row[2]) == following_id:
            return _follow_row_to_dict(follow_row)

    raise RuntimeError("Follow created but could not be fetched")



def unfollow_user(follower_id: str, following_id: str) -> dict[str, str]:
    if not is_following(follower_id, following_id):
        raise ValueError("Follow relationship not found")

    remove_follow(follower_id, following_id)
    return {"message": "User unfollowed successfully"}



def list_followers(user_id: str) -> list[dict]:
    user_row = fetch_user_by_id(user_id)
    if user_row is None:
        raise ValueError("User not found")

    followers = fetch_followers(user_id)
    return [_follow_row_to_dict(follow_row) for follow_row in followers]



def list_following(user_id: str) -> list[dict]:
    user_row = fetch_user_by_id(user_id)
    if user_row is None:
        raise ValueError("User not found")

    following = fetch_following(user_id)
    return [_follow_row_to_dict(follow_row) for follow_row in following]



def get_follow_status(follower_id: str, following_id: str) -> dict:
    return {
        "follower_id": follower_id,
        "following_id": following_id,
        "is_following": is_following(follower_id, following_id),
    }
