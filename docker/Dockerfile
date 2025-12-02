# 1. Base image
FROM python:3.12-slim

# 2. Set working directory trong container
WORKDIR /app

# 3. Copy requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tạm cài trực tiếp Flask để thử
RUN pip install flask
    
# 4. Copy toàn bộ code backend
COPY . .

# 5. Expose port 5000
EXPOSE 5000

# 6. Thiết lập biến môi trường Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# 7. Command chạy Flask
CMD ["flask", "run"]
