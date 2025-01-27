FROM python:3.13-alpine

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .

ENTRYPOINT [ "fastapi" ]
CMD [ "run", "main.py" ]