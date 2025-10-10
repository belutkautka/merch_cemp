FROM --platform=linux/amd64 python:3.13-slim
WORKDIR /root/bot

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "-u", "badbadbar_merch_bot.py"]
