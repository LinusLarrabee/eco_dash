# 使用 Python 3.8 基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到工作目录
COPY requirements.txt .

# 安装依赖并使用国内镜像源
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目文件到工作目录
COPY .. .

# 暴露应用端口
EXPOSE 8050

# 启动应用
CMD ["python", "app.py"]
