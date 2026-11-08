from flask import request, Blueprint, jsonify, session
from groq import Groq
import os
from database.db import connect_database

groq_service = Blueprint("groq_service", __name__)

groq_service.secret_key = os.environ["SESSION_KEY"]

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

@groq_service.route("/js/ai_chat", methods=["POST"])
def ai_chat():
    data = request.get_json()
    requested_category = data["requestedCategory"]
    

    print("Got data from javascript.")

    if requested_category == "firstMessage":
        response = {
            "message": "Hello! I'm Matchy, your personal AI assistant. What can I help you with?"
        }

        settings = """
            You are Job Matcher’s AI assistant. Your purpose is to help users find suitable jobs, understand job opportunities, and navigate the job-search process.

            ### Communication Style
            - Be polite, friendly, professional, and helpful.
            - Keep responses concise and easy to understand. You operate in a small chat window, so avoid unnecessarily long explanations.
            - Don't be too brief or sound rude. Provide enough information to make every response useful.
            - Use simple, natural language.
            - Avoid unnecessary introductions, repetition, and excessive bullet points.

            ### Honesty & Accuracy
            - Never lie, invent information, or pretend to know something you don't.
            - If you are unsure, say so clearly.
            - Never fabricate job listings, salaries, companies, requirements, or other details.
            - Distinguish verified information from estimates or assumptions.
            - If information is unavailable, be transparent about it.

            ### Capabilities & Limitations
            - Help users search for jobs, understand job requirements, compare opportunities, and improve their job-search approach.
            - Never claim to perform an action unless you actually can.
            - You cannot directly change user account settings, profile information, passwords, or application preferences.
            - If a user asks you to change something you cannot access, politely explain that you cannot do it. Never ask whether they would like to change settings or imply that you can do so.

            ### Conversation Rules
            - Stay focused on the user's question.
            - Ask follow-up questions only when necessary to provide an accurate answer.
            - Never pressure users into taking actions.
            - Don't pretend to be human.
            - If a request is unrelated to job searching, still try to help when possible.

            **Your goal:** Make job searching easier by providing accurate, relevant, and straightforward assistance while maintaining a polite and approachable tone.
            """

        conn = connect_database("users.db")
        c = conn.cursor()

        c.execute("INSERT INTO ai_conversations (user_id, role, content) VALUES (?, ?, ?)", (session["user_id"], "system", settings))
        c.execute("INSERT INTO ai_conversations (user_id, role, content) VALUES (?, ?, ?)", (session["user_id"], "assistant", response["message"]))

        conn.commit()
        conn.close()

    elif requested_category == "reply":
        message = data["message"]
        
        conn = connect_database("users.db")
        c = conn.cursor()

        c.execute("INSERT INTO ai_conversations (user_id, role, content) VALUES (?, ?, ?)", (session["user_id"], "user", message))
        conn.commit()

        history = [dict(obj) for obj in c.execute("SELECT role, content FROM ai_conversations WHERE user_id = ?", (session["user_id"],)).fetchall()]
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=history).choices[0].message.content
        
        c.execute("INSERT INTO ai_conversations (user_id, role, content) VALUES (?, ?, ?)", (session["user_id"], "assistant", response))
        conn.commit()
        conn.close()
    
    return jsonify(response)

@groq_service.route("/delete_ai_history", methods=["POST"])
def delete_ai_history():
    conn = connect_database("users.db")
    c = conn.cursor()

    c.execute("DELETE FROM ai_conversations WHERE user_id = ?", (session["user_id"],))
    conn.commit()
    conn.close()

    print("REMOVED!")

    return "ok"