# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# 复制 requirements.txt 到工作目录
COPY requirements.txt .

# 安装依赖并使用国内镜像源
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# Copy the rest of the working directory contents into the container
COPY . .

# Expose port 8050
EXPOSE 8050

# Run the application
CMD ["python", "index.py"]
