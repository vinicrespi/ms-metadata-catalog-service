# Metadata Service

Microserviço para gerenciamento de metadados de tabelas, desenvolvido com FastAPI, MongoDB e autenticação JWT.

## Execução com Docker Compose

O Compose inicia a API e um MongoDB em replica set, necessário para transações:

```bash
docker compose up --build
```

Serviços disponíveis:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- MongoDB: `mongodb://localhost:27017/?replicaSet=rs0`

Para encerrar os serviços:

```bash
docker compose down
```

Os dados ficam no volume `metadata-mongodb-data`. Para removê-los também:

```bash
docker compose down -v
```

## Execução local

Requisitos: Python 3.9+, `uv`, Docker e MongoDB em replica set.

```bash
uv sync --dev
docker compose up -d mongo mongo-init
uv run uvicorn app.main:app --reload
```

Variáveis de ambiente:

```env
DATABASE_URL=mongodb://localhost:27017/?replicaSet=rs0
DATABASE_NAME=metadata_catalog
SECRET_KEY=uma-chave-com-pelo-menos-32-caracteres
```

`SECRET_KEY` deve ter pelo menos 32 bytes para uso seguro com HS256.

## Autenticação

Crie um usuário:

```bash
curl -X POST http://localhost:8000/auth/users \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"senha-segura-123"}'
```

Obtenha um token:

```bash
curl -X POST http://localhost:8000/auth/token \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"senha-segura-123"}'
```

Use o token nos endpoints de Metadata:

```bash
curl http://localhost:8000/metadata \
  -H 'Authorization: Bearer <access_token>'
```

`/health`, `/auth/users` e `/auth/token` são públicos. Os endpoints de Metadata exigem Bearer token.

## Endpoints

| Método | Endpoint | Autenticação | Descrição |
| --- | --- | --- | --- |
| `GET` | `/health` | Não | Verifica a saúde da aplicação |
| `POST` | `/auth/users` | Não | Cria um usuário |
| `POST` | `/auth/token` | Não | Autentica e retorna JWT |
| `POST` | `/metadata` | Sim | Cria uma versão do metadata e registra o histórico |
| `GET` | `/metadata` | Sim | Lista os metadados |
| `GET` | `/metadata/{metadata_id}` | Sim | Busca metadata por ID |
| `PUT` | `/metadata/{metadata_id}` | Sim | Atualiza metadata parcialmente |
| `DELETE` | `/metadata/{metadata_id}` | Sim | Remove metadata |
| `GET` | `/metadata/{metadata_id}/histories` | Sim | Lista o histórico do metadata |

## Payload de Metadata

```json
{
  "table_name": "vendas_diarias",
  "description": "Dados consolidados de vendas",
  "domain": "Financeiro",
  "storage": {
    "format": "parquet",
    "storage_path": "s3://meu-bucket/financeiro/vendas_diarias/",
    "is_partitioned": true
  },
  "current_version": 3,
  "current_schema": [
    {
      "field": "id_venda",
      "type": "INT",
      "nullable": false,
      "description": "ID unico da venda"
    }
  ],
  "owner": "equipe_dados_fin",
  "created_at": "2025-01-10T10:00:00Z",
  "updated_at": "2026-09-23T09:00:00Z",
  "data_classification": "restrito"
}
```

Ao criar um metadata, a API salva o documento em `tab_metadata` e registra a alteração em `tab_schema_history` dentro da mesma transação MongoDB.

## Postman

Importe [postman/metadata-catalog.postman_collection.json](postman/metadata-catalog.postman_collection.json).

Execute os requests nesta ordem:

1. `Create user - 201`
2. `Login - 200`
3. Os requests de `Metadata CRUD`

O login salva automaticamente o JWT na variável `accessToken`, usada como Bearer token pelos requests protegidos. A coleção também contém casos de erro `404` e `422`.

## Arquitetura

O projeto segue uma arquitetura hexagonal:

- `app/domain`: modelos e regras de domínio.
- `app/application`: casos de uso e ports.
- `app/adapters/inbound`: rotas FastAPI e handlers de erro.
- `app/adapters/outbound`: adapters MongoDB e mappers BSON.
- `app/infrastructure`: configuração, segurança, banco e dependências.

Erros são retornados em formato padronizado:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": []
  }
}
```

## Testes

```bash
uv run pytest
```

Os testes unitários usam mocks e repositórios em memória. Os testes de integração locais exigem o MongoDB iniciado pelo Compose.
