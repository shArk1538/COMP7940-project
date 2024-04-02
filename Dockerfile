FROM python:3.11

RUN apt-get update -y && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install update
RUN pip install -r requirements.txt

ENV PATH="/usr/local/bin/ffmpeg:${PATH}"
ENV Bot_Token=6714468890:AAGftjmq-FEZi8vdJ0m-e_2Kku8q07RjuDE
ENV GPT_BasicURL=https://chatgpt.hkbu.edu.hk/general/rest
ENV GPT_ModelName=gpt-35-turbo
ENV GPT_APIversion=2024-02-15-preview
ENV GPT_Token=06439077-ecaf-42ff-b64a-51698545e8ef
ENV Map_Key=AIzaSyBbqSQLhElKvrKs00uaG6pP6acy_fq99ok
ENV DB_User=user1
ENV DB_Pswd=@Xyx20000112

CMD python chatbot.py


