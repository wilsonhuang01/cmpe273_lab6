FROM python:3.12-slim
WORKDIR /app
COPY inventory/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY inventory/inventory.py ./inventory.py
COPY client/client.py ./client.py
ENV PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 5001
CMD ["python", "inventory.py"]
