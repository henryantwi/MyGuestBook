import os
from datetime import datetime

import pytz
from dotenv import load_dotenv
from fasthtml.common import *
from supabase import create_client

# Load environment variables
load_dotenv()

MAX_NAME_CHAR = 30
MAX_MESSAGE_CHAR = 60
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)


app, rt = fast_app(
    hdrs=(Link(rel='icon', type='assets/x-icon', href='/assets/book.png'),),
)


def get_gmt_time() -> str:
    return datetime.now(pytz.utc).strftime(TIMESTAMP_FORMAT)


def add_message(name: str, message: str) -> None:
    supabase.table("MyGuestBook").insert(
        {"name": name, "message": message, "timestamp": get_gmt_time()}
    ).execute()


def get_messages() -> list:
    # Sort by "id" in descending order to get the latest messages first
    response = (
        supabase.table("MyGuestBook").select("*").order("id", desc=True).execute()
    )
    return response.data


def render_message(entry):
    return Article(
        Header(f'Name: {entry["name"]}'),
        P(f'Message: {entry["message"]}'),
        Footer(Small(f'Posted on: {entry["timestamp"]}')),
    )


def render_message_list():
    messages: list = get_messages()
    return Div(
        *[render_message(entry) for entry in messages],
        id="message-list",
    )


def render_content():
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="name",
                placeholder="Your name",
                required=True,
                maxlength=MAX_NAME_CHAR,
            ),
            Input(
                type="text",
                name="message",
                placeholder="Your message",
                required=True,
                maxlength=MAX_MESSAGE_CHAR,
            ),
            Button("Submit", type="submit"),
            # role="group",
        ),
        method="post",
        hx_post="/submit-message",  # Send POST request to the /submit-message endpoint
        hx_target="#message-list",  # Update the content of the element with the id "message-list"
        hx_swap="outerHTML",  # Replace the entire content of the target with the response
        hx_on__after_request="this.reset()",  # Reset the form after a successful submission
    )
    return Div(
        P(Em("Write something nicess!")),
        form,
        Div(
            "Made with ❤️ by ",
            A("Henry", href="https://www.github.com/henryantwi", target="_blank"),
        ),
        Hr(),
        render_message_list(),
    )


@rt("/")
def get():
    return Titled("Henry's GuestBook 📖", render_content())


@rt("/submit-message", methods=["POST"])
def post(name: str, message: str):
    add_message(name.capitalize(), message.title())
    return render_message_list()


serve()
