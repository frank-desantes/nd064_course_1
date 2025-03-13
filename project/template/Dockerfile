FROM python:3.8
LABEL maintainer="Frank Pohlen"

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN python init_db.py

# command to run on container start
CMD [ "python", "app.py" ]
