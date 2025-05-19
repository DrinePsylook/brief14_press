FROM python:3.9

WORKDIR /code

# Copier tous les fichiers d'un coup
COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /code/app

CMD ["python", "populate.py"]