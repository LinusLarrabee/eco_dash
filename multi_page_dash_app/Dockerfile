# 使用 Python 3.8 基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . .

# 安装依赖
RUN pip install pandas dash

# 暴露应用端口
EXPOSE 8050

# 启动应用
CMD ["python", "app.py"]
