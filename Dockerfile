FROM python:3.13-alpine

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt

COPY src/ .

# alternative 
# ENTRYPOINT [ "fastapi" ]
# CMD [ "run", "main.py" ]

CMD [ "fastapi", "run", "main.py" ]