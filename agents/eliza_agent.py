
# Eliza Agent Loop - Langchain-powered
import os
import time
from dotenv import load_dotenv
from langchain.llms import OpenAI

load_dotenv()
api_key = os.getenv("VITE_OPEN_AI_API_KEY")
llm = OpenAI(api_key=api_key, temperature=0.3)

def simulate_mining_data():
    return {
        "user_id": "user123",
        "hashrate": 870,
        "xmr_mined": 0.014
    }

def generate_proposal(data):
    prompt = f"""
    A user has mined {data['xmr_mined']} XMR at a rate of {data['hashrate']} H/s.
    Should the DAO grant them a reward or initiate a governance vote?
    Respond with: [REWARD], [VOTE], or [IGNORE] and a one-sentence justification.
    """
    return llm.predict(prompt)

if __name__ == "__main__":
    while True:
        mining = simulate_mining_data()
        result = generate_proposal(mining)
        print("Eliza Agent Decision:", result.strip())
        time.sleep(60)
