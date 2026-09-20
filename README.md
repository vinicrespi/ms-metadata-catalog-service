# Metadata Catalog Service

Microserviço para cadastro e consulta de metadados de tabelas, desenvolvido com FastAPI e MongoDB.

## Running locally

O serviço precisa de uma instância MongoDB disponível. As configurações podem ser definidas pelas variáveis `MONGODB_URL` e `MONGODB_DATABASE`.

Valores utilizados localmente:

```text
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=metadata_catalog
```

### 1. Inicie o Colima

No macOS, o Colima fornece a máquina virtual necessária para executar o Docker:

```bash
colima start
docker info
```

Se ainda não tiver as ferramentas instaladas:

```bash
brew install colima docker
```

### 2. Inicie o MongoDB com Docker

Crie o container na primeira execução:

```bash
docker run -d \
	--name metadata-mongodb \
	-p 27017:27017 \
	-v metadata-mongodb-data:/data/db \
	mongo:8
```

Confirme se o container está ativo:

```bash
docker ps
```

Nas próximas execuções, caso o container já exista:

```bash
docker start metadata-mongodb
```

Para parar o MongoDB:

```bash
docker stop metadata-mongodb
```

### 3. Inicie a API

```bash
uv sync --dev
export MONGODB_URL=mongodb://localhost:27017
export MONGODB_DATABASE=metadata_catalog
uv run fastapi dev app/main.py
```

A documentação interativa está disponível em `http://localhost:8000/docs`.

Valide a API antes de usar o Postman:

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{"status": "ok"}
```

## Endpoints

| Método | Endpoint | Descrição |
| --- | --- | --- |
| `GET` | `/health` | Verifica a saúde da aplicação |
| `POST` | `/metadata` | Cria um metadado |
| `GET` | `/metadata` | Lista os metadados |
| `GET` | `/metadata/{metadata_id}` | Busca um metadado por ID |
| `PUT` | `/metadata/{metadata_id}` | Atualiza um metadado |
| `DELETE` | `/metadata/{metadata_id}` | Remove um metadado |

Exemplo de payload:

```json
{
	"name": "payments",
	"description": "Payment table",
	"owner": "finance",
	"source_system": "postgres",
	"payload": {
		"columns": ["id", "customer_id", "amount"]
	}
}
```

## Postman

A coleção está disponível em [postman/metadata-catalog.postman_collection.json](postman/metadata-catalog.postman_collection.json).

Para executar:

1. Inicie o Colima.
2. Inicie o MongoDB com Docker.
3. Inicie a API.
4. No Postman, selecione **Import** e escolha a coleção.
5. Execute `Health check`.
6. Execute `Create metadata`.
7. Execute os demais requests do grupo `Metadata CRUD`.

O request de criação salva automaticamente o ID retornado na variável `metadataId`. A coleção também contém casos de erro `404` e `422`.

## Architecture

The project follows hexagonal architecture:

- `app/domain`: domain models and validation rules.
- `app/application`: use cases and outbound ports, independent from infrastructure.
- `app/adapters/inbound`: FastAPI HTTP adapter.
- `app/adapters/outbound`: MongoDB adapter that implements the repository port.
- `app/infrastructure/config.py`: external settings loaded from environment variables.
- `app/infrastructure/database.py`: composition root and MongoDB lifecycle/dependency wiring.
- `app/infrastructure/dependencies.py`: FastAPI dependency providers.

## Tests

```bash
uv run pytest
```

Os testes usam um repositório em memória e mocks, portanto não precisam de uma instância MongoDB ativa.

Para executar testes específicos:

```bash
uv run pytest tests/test_api.py -q
uv run pytest tests/test_service.py -q
```
