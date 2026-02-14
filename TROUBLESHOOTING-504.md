# 🔍 Diagnóstico - 504 Gateway Timeout

## Problema
`https://tecnogatt.kaizen.dev.br/catedral/auth/login` retorna **504 Gateway Timeout**

Isso significa que o **nginx recebe a requisição**, mas não consegue se comunicar com o Flask.

---

## ✅ Checklist de Diagnóstico

### 1️⃣ Verificar se o Flask está rodando

No servidor (72.60.0.141), execute:

```bash
# Ver processos Python rodando
ps aux | grep python

# Verificar se porta 5000 está em uso
netstat -tlnp | grep 5000
# ou
lsof -i :5000
```

**Esperado:** Deve mostrar um processo Python na porta 5000

**Se não estiver rodando:**
```bash
cd /caminho/para/igreja-em-foco-backend
uv run python server.py
```

---

### 2️⃣ Verificar configuração nginx

```bash
# Ver configuração de /catedral
nginx -T | grep -A 20 "location /catedral"

# Testar configuração
sudo nginx -t

# Ver logs de erro
sudo tail -f /var/log/nginx/error.log
```

**Configuração correta deve ser:**
```nginx
location /catedral {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_connect_timeout 60s;
    proxy_read_timeout 60s;
}
```

---

### 3️⃣ Testar conexão local do servidor

**No servidor**, teste se o Flask responde localmente:

```bash
# Testar raiz
curl -v http://localhost:5000/

# Testar com /catedral (DispatcherMiddleware)
curl -v http://localhost:5000/catedral/

# Testar endpoint de login diretamente
curl -v -X POST http://localhost:5000/catedral/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'
```

**Esperado:** 
- Se retornar HTML/JSON = ✅ Flask está respondendo
- Se timeout/conexão recusada = ❌ Flask não está rodando

---

### 4️⃣ Verificar logs do Flask

```bash
# Ver output do servidor Flask
# Se rodando em background, verificar logs

# Ou rodar manualmente para ver errors
cd /caminho/para/igreja-em-foco-backend
uv run python server.py
```

---

### 5️⃣ Verificar variáveis de ambiente

No servidor, conferir `.env`:

```bash
cat .env | grep APPLICATION_SUBPATH
```

**Deve ter:**
```
APPLICATION_SUBPATH=/catedral
```

---

## 🔧 Soluções Rápidas

### Solução 1: Reiniciar Flask

```bash
# Parar processo atual (se estiver rodando)
pkill -f "python.*server.py"

# Iniciar novamente
cd /caminho/para/igreja-em-foco-backend
uv run python server.py

# Ou com nohup para rodar em background
nohup uv run python server.py > server.log 2>&1 &
```

### Solução 2: Aumentar timeout do nginx

Se o Flask demora para responder, aumente o timeout:

```nginx
location /catedral {
    proxy_pass http://127.0.0.1:5000;
    # ... outros headers
    
    # Aumentar timeouts
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
}
```

Depois:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Solução 3: Verificar firewall

```bash
# Ver regras de firewall
sudo iptables -L -n

# Se necessário, permitir conexões locais na porta 5000
sudo ufw allow from 127.0.0.1 to any port 5000
```

---

## 📊 Status Esperado

Quando tudo estiver funcionando:

1. ✅ `ps aux | grep python` mostra servidor rodando
2. ✅ `netstat -tlnp | grep 5000` mostra porta 5000 em LISTEN
3. ✅ `curl localhost:5000/catedral/` retorna resposta (não timeout)
4. ✅ Nginx consegue fazer proxy para o Flask
5. ✅ `https://tecnogatt.kaizen.dev.br/catedral/` funciona

---

## 🚨 Se Nada Funcionar

Execute este script de diagnóstico completo no servidor:

```bash
#!/bin/bash
echo "=== DIAGNÓSTICO COMPLETO ==="
echo ""
echo "1. Processos Python:"
ps aux | grep python
echo ""
echo "2. Porta 5000:"
netstat -tlnp | grep 5000
echo ""
echo "3. Teste local Flask:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5000/catedral/
echo ""
echo "4. Nginx config /catedral:"
nginx -T 2>/dev/null | grep -A 15 "location /catedral"
echo ""
echo "5. Últimos erros nginx:"
tail -n 20 /var/log/nginx/error.log
echo ""
echo "=== FIM ==="
```

Envie o resultado para análise!
