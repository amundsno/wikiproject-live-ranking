# Transpile TS to JS
FROM node:23.10 as build
WORKDIR /app
RUN npm install typescript
COPY tsconfig.json ./
COPY ./src/ ./src/
RUN npx tsc

FROM nginx:1.27.4
COPY --from=build /app/src/ /usr/share/nginx/html/
COPY ./nginx.conf /etc/nginx/conf.d/default.conf