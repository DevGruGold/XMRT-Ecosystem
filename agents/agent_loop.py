# ðŸ§  Eliza Agent Loop - Mines hashrate and triggers XMRT reward record()

import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from time import sleep

load_dotenv()
openai_key = os.getenv("VITE_OPEN_AI_API_KEY")

def fetch_hashrate():
    return 0.0247, 1200  # example stub (XMR mined, hashrate)

def record_to_contract(xmr, hashrate):
    print(f"[ELIZA] Recording reward: {xmr} XMR @ {hashrate} H/s")

def run_agent():
    llm = OpenAI(api_key=openai_key, temperature=0.3)
    while True:
        mined, rate = fetch_hashrate()
        prompt = f"User has mined {mined} XMR with hashrate {rate}. Should reward be issued?"
        decision = llm.predict(prompt)
        if "yes" in decision.lower():
            record_to_contract(mined, rate)
        sleep(60)

if __name__ == "__main__":
    run_agent()
