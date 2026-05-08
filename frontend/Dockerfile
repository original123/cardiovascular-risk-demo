# 阶段一：构建 Vue 前端
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# 阶段二：nginx 静态服务
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 移除默认的 nginx 配置（避免端口冲突）
RUN rm -f /etc/nginx/conf.d/default.conf.bak

EXPOSE 4000

CMD ["nginx", "-g", "daemon off;"]
