from dataclasses import dataclass
from typing import List, Any
import sys
import os
import argparse
import requests
from fastmcp import FastMCP


def main():
    parser = argparse.ArgumentParser(
        description="Goodreads MCP CLI - Interface for Goodreads integration"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    get_books_parser = subparsers.add_parser("get-books", help="Get books from Goodreads")
    get_books_parser.add_argument("--email", required=True, help="Email address")
    get_books_parser.add_argument("--password", required=True, help="Password")
    get_books_parser.add_argument("--host", default="127.0.0.1:8000", help="Host URL (default: 127.0.0.1:8000)")

    args = parser.parse_args()

    if args.command == "get-books":
        try:
            response = get_goodreads_books(args.email, args.password, args.host)
            print(f"Authenticated! Profile ID: {response.profile_id}")
            print(f"Found {len(response.bundles)} books")
            for bundle in response.bundles:
                print(f"- {bundle.title} by {bundle.author} (★{bundle.rating})")
        except AuthException as e:
            print(f"Failed to get books: {e}")
            sys.exit(1)
            
    else:
        mcp()


@dataclass()
class Bundle(object):
    cover: str
    title: str
    author: str
    rating: float


@dataclass
class AuthResponse(object):
    profile_id: str
    bundles: List[Bundle]


class AuthException(Exception):
    msg: str


class AuthError(AuthException):
    def __init__(self, msg):
        self.msg = msg


def get_goodreads_books(email: str, password: str, host: str = "127.0.0.1:8000") -> AuthResponse:
    payload = {
        "brand_name": "goodreads",
        "state": {
            "inputs": {
                "email": email,
                "password": password,
            }
        },
    }

    try:
        response = requests.post(f"http://{host}/auth/goodreads", json=payload)
        response_json = response.json()
    except requests.exceptions.ConnectionError:
        raise AuthError(
            f"Cannot connect to getgather service at {host}. "
            "Please ensure getgather is running:\n"
            "docker run -p 8000:8000 getgather/dax"
        )

    if response.status_code != 200:
        raise AuthError(response.text)

    error_msg = response_json["state"]["error"]
    if error_msg:
        raise AuthError(msg=error_msg)

    profile_id = response_json["profile_id"]
    bundles = get_bundle(response_json["extract_result"]["bundles"])
    return AuthResponse(profile_id=profile_id, bundles=bundles)


def get_bundle(bundles: List[Any]) -> List[Bundle]:
    bundles_response = []

    for bundle in bundles:
        if not isinstance(bundle["content"], list):
            continue

        for content in bundle["content"]:
            bundles_response.append(
                Bundle(
                    cover=content["cover"],
                    title=content["title"],
                    author=content["author"],
                    rating=float(content["rating"]),
                )
            )

    return bundles_response


def mcp():
    mcp_server = FastMCP("Goodreads MCP")
    
    def get_auth_response():
        """Helper function to get cached auth response or authenticate if needed."""
        email = os.getenv("GOODREADS_EMAIL")
        password = os.getenv("GOODREADS_PASSWORD")
        
        if not email or not password:
            raise AuthError("GOODREADS_EMAIL and GOODREADS_PASSWORD environment variables must be set")
        
        host = os.getenv("GETGATHER_URL", "127.0.0.1:8000")
        return get_goodreads_books(email, password, host)
    
    @mcp_server.tool()
    def get_books() -> dict:
        """
        Get books from Goodreads using configured credentials.
        Credentials should be set via environment variables GOODREADS_EMAIL, and GOODREADS_PASSWORD.
        
        Returns:
            Dictionary containing profile_id and list of books
        """
        try:
            response = get_auth_response()
            return {
                "profile_id": response.profile_id,
                "books": [
                    {
                        "title": bundle.title,
                        "author": bundle.author,
                        "rating": bundle.rating,
                        "cover": bundle.cover
                    }
                    for bundle in response.bundles
                ]
            }
        except AuthException as e:
            return {"error": str(e.msg)}
    
    
    mcp_server.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
