FROM node:20

WORKDIR /app

COPY apps/frontend/package*.json ./
RUN npm install

COPY apps/frontend .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
