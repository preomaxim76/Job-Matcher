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

        settings = ""

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
        
        print(history)
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=history).choices[0].message.content
        
        session["history"].append({"role": "assistant", "content": response})
        c.execute("INSERT INTO ai_conversations (user_id, role, content) VALUES (?, ?, ?)", (session["user_id"], "assistant", response))
        conn.commit()
        conn.close()
    
    return jsonify(response)
