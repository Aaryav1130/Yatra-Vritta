from flask import Flask, request, jsonify
from nltk.chat.eliza import eliza_chat
from nltk.chat.iesha import iesha_chat
from nltk.chat.rude import rude_chat
from nltk.chat.suntsu import suntsu_chat
from nltk.chat.zen import zen_chat
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "").lower()

    if "medical" in user_message or "tourism" in user_message:
        response = "Medical tourism helps patients travel abroad for quality healthcare at affordable costs."

    elif "mice" in user_message or "conference" in user_message:
        response = "MICE stands for Meetings, Incentives, Conferences and Exhibitions."

    elif "wedding" in user_message or "marriage" in user_message:
        response = "Destination weddings allow couples to celebrate their marriage in attractive travel destinations."

    elif "business" in user_message:
        response = "Business tourism involves travel for professional meetings and corporate events."

    else:
        response = "I can answer questions about Medical Tourism, MICE and Destination Weddings."

    return jsonify({"response": response})

@app.route('/test')
def test():
    return jsonify({"status": "working"})
    
if __name__ == '__main__':
    app.run(debug=True)
