# What beats Rock?

**Empowering the classic what-beats-rock game with Generative AI, build with FastAPI, Redis and Docker**

# Overview
"What-beats-rock" is an AI enhanced word game, where users attempt to beat rock in a conceptual or metaphorical sense. This is then evaluated by the genAI backend, providing AI-generated feedback, in a serious or cheery tone as chosen by user.

## Tech Stack
-**Frontend**: Streamlit   
-**Backend**: FastAPI (Python)  
-**LLM**: Gemini   
-**Database**: Redis  
-**Containerization**: Docker   


## Project Structure

 * [frontend](./frontend)
   * [Dockerfile](./frontend/Dockerfile)
   * [requirements.txt](./frontend/requirements.txt)
   * [frontend.py](./frontend/frontend.py)
 * [backend](./backend)
   * [requirements.txt](./backend/requirements.txt)
   * [__pycache__](./backend/__pycache__)
     * [test.cpython-310.pyc](./backend/__pycache__/test.cpython-310.pyc)
     * [redis_client.cpython-310.pyc](./backend/__pycache__/redis_client.cpython-310.pyc)
     * [main.cpython-310.pyc](./backend/__pycache__/main.cpython-310.pyc)
   * [Dockerfile](./backend/Dockerfile)
   * [redis_client.py](./backend/redis_client.py)
   * [main.py](./backend/main.py)
 * [docker-compose.yml](./docker-compose.yml)

## Set up Instructions
1. `git clone https://github.com/Eros483/arnab-mandal-wasserstoff-AiInternTask.git`
2. `cd arnab-mandal-wasserstoff-AiInternTask`
3. `docker-compose up --build`
