# docker build --progress=plain -t qufudcj/openldapui-iam:v1 .
FROM python:3.10.16-alpine3.21
# 安装nginx
RUN apk add --no-cache nginx && ls /etc/nginx
# nginx配置文件
RUN echo 'server  {' > /etc/nginx/http.d/openldapui-iam.conf && \
    echo '    listen       80;' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '    index index.html index.htm index.php;' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '    # 你手动编译或下载编译好的web目录' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '    root  /openldapui-iam/web-iam-dist;' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '    # /api是后端接口' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '    location /api {' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '        if ($request_method = 'OPTIONS') {' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '             return 200;' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '        }' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '        # 酌情修改997端口号' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '        proxy_pass   http://127.0.0.1:997;' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '        proxy_next_upstream off;' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '        proxy_set_header Upgrade $http_upgrade;' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '        proxy_set_header Connection "upgrade";' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '    }' >> /etc/nginx/http.d/openldapui-iam.conf && \
    echo '}' >> /etc/nginx/http.d/openldapui-iam.conf
RUN rm -f /etc/nginx/http.d/default.conf
# 设定时区
RUN apk add --no-cache tzdata
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone && date
# 设置中文环境, musl库无需安装glibc
RUN apk add --no-cache musl-locales
# 这样设置/etc/profile似乎不起作用, 需要用ENV
RUN echo "export LANG=zh_CN.UTF-8" >> /etc/profile
RUN echo "export LC_ALL=zh_CN.UTF-8" >> /etc/profile && source /etc/profile
# 如果一切设置正确, 应该显示 zh_CN.UTF-8 等相关设置
# RUN localedef -i zh_CN -f UTF-8 zh_CN.UTF-8
ENV LANG=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8
RUN locale
# 安装redis
RUN apk add --no-cache redis
# 是程序启用redis
ENV UIIAM_DB_MODE=redis
# 创建主目录
RUN mkdir /openldapui-iam
# 拷贝前端文件
COPY web-iam-dist /openldapui-iam/web-iam-dist
# 拷贝后端文件
COPY api-iam /openldapui-iam/api-iam
# 安装python依赖
RUN pip install --no-cache-dir -r /openldapui-iam/api-iam/requirements.txt
RUN pip cache purge

# 设置启动相关
RUN echo "#!/bin/sh" > /openldapui-iam/start.sh && \
    echo "# 启动 Nginx" >> /openldapui-iam/start.sh && \
    # echo "nginx -g 'daemon off;' &" >> /openldapui-iam/start.sh && \
    echo "nginx" >> /openldapui-iam/start.sh && \
    echo "# 启动 redis" >> /openldapui-iam/start.sh && \
    echo "echo 'daemonize yes' | redis-server -" >> /openldapui-iam/start.sh && \
    echo "# 切换到指定目录并启动 Python API" >> /openldapui-iam/start.sh && \
    echo "cd /openldapui-iam/api-iam && python OpenLdapUi-IAM-api.py" >> /openldapui-iam/start.sh
RUN chmod +x /openldapui-iam/start.sh
# 工作目录
WORKDIR /openldapui-iam
CMD ["/openldapui-iam/start.sh"]