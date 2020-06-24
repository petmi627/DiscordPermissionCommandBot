FROM python:3

MAINTAINER Mike Peters "mike@skylake.me"

COPY ./requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

COPY ./discord_permissions_command_bot.py /bot.py
WORKDIR /

CMD ["python", "bot.py"]