from flask import Blueprint
from groq import Groq
import os

groq_service = Blueprint("groq_service", __name__)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

@groq_service.route("/ai_chat", methods=["POST"])
def ai_chat():
    # TODO
    pass