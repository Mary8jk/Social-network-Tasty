FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

COPY recipes/management/commands/import_data.py /app/recipes/management/commands/

COPY data/ingredients.csv /app/

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:9001", "foodgram.wsgi"] 