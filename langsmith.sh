source .env
service docker start
export SSL_PATH="/root/ssl"
export NGINX_CONF_PATH="/root/code/langgraph/nginx/nginx.conf"
cd nginx && docker-compose down && docker-compose rm && docker-compose up -d && cd ..
echo "Acesse a URL:"
echo "https://smith.langchain.com/studio/?baseUrl=https://langgraph.local"
langgraph dev --config langgraph.json --host 0.0.0.0