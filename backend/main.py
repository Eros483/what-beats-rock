from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
from pydantic import BaseModel
from better_profanity import profanity
from dotenv import load_dotenv
import os
from openai import OpenAI
from backend.redis_client import r
import fnmatch

load_dotenv()
openai_api_key=os.getenv("OPENAI_API_KEY")
client=OpenAI(api_key=openai_api_key)

class LinkedList:
    def __init__(self, redis_client, user_id):
        self.redis=redis_client
        self.user_key=f"history: {user_id}"

    def add(self, guess: str)-> bool:
        '''guess=guess.lower()
        if guess in self.guesses:
            return False
        self.guesses.append(guess)
        return True'''
        if self.redis.sismember("all_guesses", guess):
            return False
        
        self.redis.rpush(self.user_key, guess)
        self.redis.sadd("all_guesses", guess)
        return True
    
    def history(self):
        return self.redis.lrange(self.user_key, -5, -1)

user_sessions={}

async def check_with_ai(seed: str, guess: str, persona: str)->bool:

    persona_prompt={
        "serious": "You're a serious, concise, logical AI game refree.",
        "cheery": "You're a silly, cheerful and funny game host who makes decisions."
    }[persona]

    prompt=f""""{persona_prompt}
Does {guess} beat {seed}? just reply YES or NO. No other texts.
""" 
    
    cache_key=f"verdict:{persona}:{seed.lower()}:{guess.lower()}"
    cached=r.get(cache_key)
    if cached:
        return cached.strip().upper()=="YES"
    
    '''response=client.responses.create(
        model="gpt-3.5-turbo",
        instructions=persona_prompt,
        input=prompt,
        temperature=0,
    )
    print(response.output_text)'''
    verdict="YES"

    r.set(cache_key, verdict, ex=86400)
    return verdict=="YES"

profanity.load_censor_words()

app=FastAPI()

class GuessRequest(BaseModel):
    seed_word: str
    guess: str
    user_id: str
    persona: str="serious"

user_sessions={}

@app.post("/guess")
async def make_guess(request: GuessRequest):
    if profanity.contains_profanity(request.guess):
        return{
            "error": "profanity detected in guess, please retry."
        }

    linked_list=LinkedList(r, request.user_id)

    if not linked_list.add(request.guess.lower()):
        return{
            "game_over": True, 
            "message": f"{request.guess} was already guessed. Game over.",
            "history": linked_list.history()
        }
    
    verdict=await check_with_ai(request.seed_word, request.guess, request.persona)

    r.incr(request.guess.lower())
    count=int(r.get(request.guess.lower()) or 0)

    if verdict:
        return {
            "game_over":False,
            "message": f"{request.guess} beats {request.seed_word}.",
            "times_guessed": count,
            "score": r.llen(linked_list.user_key),
            "history": linked_list.history()
        }
    
    else:
        return{
            "game_over": False,
            "message": f"{request.guess} does not beat {request.seed_word}",
            "score": r.llen(linked_list.user_key),
            "history":linked_list.history()
        }

@app.get("/history/{user_id}")
async def get_history(user_id :str):
    linked_list=LinkedList(r, user_id)
    return {"last_5_guesses": linked_list.history()}

@app.get("/")
async def root():
    return {"message": "Rock game API is running"}


async def rate_limit_middleware(request: Request, call_next):
    ip=request.client.host
    key=f"ratelimit:{ip}"
    count=r.incr(key)
    if count==1:
        r.expire(key, 60)

    if count>60:
        return JSONResponse(status_code=429, content={"error": "Rate limited"})
    return await call_next(request)

@app.post("/reset/{user_id}")
async def reset_user(user_id: str):
    r.delete(f"history: {user_id}")
    r.delete(f"user_guesses: {user_id}")

    for key in r.scan_iter("history:*"):
        r.delete(key)

    for key in r.scan_iter("user_guesses:*"):
        r.delete(key)

    r.delete("all_guesses")

    return {"status": "global reset succesful"}