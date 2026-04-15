# GraphQL Tools Reference

Detailed API patterns, endpoint configurations, and usage notes for each supported GraphQL system. Read this file when you need system-specific details beyond what SKILL.md covers.

## Hasura GraphQL Engine

**Endpoints:**
- GraphQL API: `{base}/v1/graphql`
- Metadata API: `{base}/v1/metadata`
- Schema API: `{base}/v2/query`
- Health: `{base}/healthz`

**Authentication:**
- Admin: `x-hasura-admin-secret` header (NOT `Authorization`)
- JWT: `Authorization: Bearer <token>` with Hasura claims in `https://hasura.io/jwt/claims`
- Webhook: configure via `HASURA_GRAPHQL_AUTH_HOOK` env var

**Common metadata operations:**
```json
{"type": "pg_track_table", "args": {"source": "default", "table": {"schema": "public", "name": "users"}}}
{"type": "pg_create_select_permission", "args": {"source": "default", "table": {"schema": "public", "name": "users"}, "role": "user", "permission": {"columns": ["id", "name"], "filter": {"id": {"_eq": "X-Hasura-User-Id"}}}}}
{"type": "export_metadata", "version": 2, "args": {}}
```

**Subscription format (over WebSocket):**
```json
{"type": "start", "id": "1", "payload": {"query": "subscription { users { id name } }"}}
```

## PostGraphile (Graphile Crystal)

**Default endpoint:** `http://localhost:5000/graphql` (configurable)

**Inflection rules:**
- Tables: `snake_case` -> `PascalCase` (e.g., `user_accounts` -> `UserAccount`)
- Columns: `snake_case` -> `camelCase` (e.g., `first_name` -> `firstName`)
- Connections: `{tableName}Connection` with `edges[].node` pattern
- Mutations: `create{Type}`, `update{Type}ById`, `delete{Type}ById`

**Smart comments for customization:**
```sql
COMMENT ON TABLE users IS E'@name person\n@omit delete';
COMMENT ON COLUMN users.email IS E'@name emailAddress';
```

**Row-level security:** PostGraphile respects PostgreSQL RLS policies when `pgSettings` passes the current role.

## Apollo Router / Federation

**Supergraph config format (supergraph.yaml):**
```yaml
subgraphs:
  accounts:
    routing_url: http://accounts:4001/graphql
    schema:
      file: ./schemas/accounts.graphql
  products:
    routing_url: http://products:4002/graphql
    schema:
      file: ./schemas/products.graphql
```

**Key federation directives:**
```graphql
type User @key(fields: "id") {
  id: ID!
  name: String!
}

extend type User @key(fields: "id") {
  id: ID! @external
  reviews: [Review!]!
}
```

**Router config (router.yaml):**
```yaml
supergraph:
  listen: 0.0.0.0:4000
  path: /
cors:
  origins:
    - https://studio.apollographql.com
headers:
  all:
    request:
      - propagate:
          named: authorization
```

## GraphQL Mesh

**Mesh config (.meshrc.yaml):**
```yaml
sources:
  - name: RestAPI
    handler:
      openapi:
        source: https://api.example.com/openapi.json
        baseUrl: https://api.example.com
  - name: gRPCService
    handler:
      grpc:
        endpoint: grpc.example.com:50051
        protoFilePath: ./proto/service.proto
  - name: PostgresDB
    handler:
      postgraphile:
        connectionString: postgres://user:pass@host:5432/db

transforms:
  - prefix:
      value: API_
      includeRootOperations: true

serve:
  port: 4000
```

**Source handlers:** openapi, grpc, postgraphile, graphql, json-schema, soap, thrift, mongoose, neo4j, odata

## WunderGraph

**Config (wundergraph.config.ts):**
```typescript
export default configureWunderGraphApplication({
  apis: [
    introspect.graphql({ apiNamespace: "weather", url: "https://weather-api.example.com/graphql" }),
    introspect.openApi({ apiNamespace: "stripe", source: { kind: "file", filePath: "./stripe-openapi.yaml" } }),
    introspect.postgresql({ apiNamespace: "db", databaseURL: "postgresql://..." }),
  ],
});
```

**Operations (`.wundergraph/operations/`):** Define queries/mutations as `.graphql` files. WunderGraph generates type-safe client code.

## Tailcall

**Config format:** `.graphql` files with custom directives.

**Core directives:**
```graphql
schema @server(port: 8000, hostname: "0.0.0.0") @upstream(baseURL: "https://api.example.com") {
  query: Query
}

type Query {
  users: [User] @http(path: "/users")
  user(id: Int!): User @http(path: "/users/{{.args.id}}")
  posts: [Post] @http(path: "/posts", query: [{key: "limit", value: "100"}])
}

type User {
  id: Int!
  name: String!
  posts: [Post] @http(path: "/users/{{.value.id}}/posts")
}
```

**Advanced directives:** `@grpc`, `@graphQL` (proxy to another GQL endpoint), `@expr` (computed fields), `@cache`, `@modify`

## Grafbase

**Schema (grafbase/schema.graphql):**
```graphql
extend schema @auth(providers: [{ type: jwt, issuer: "{{ env.ISSUER_URL }}", secret: "{{ env.JWT_SECRET }}" }])

type User @model {
  name: String!
  email: String! @unique
  posts: [Post]
}
```

**Federation support:** Grafbase acts as a GraphQL gateway composing multiple subgraphs. Configure via `grafbase.toml`.

## GitHub GraphQL API

**Endpoint:** `https://api.github.com/graphql`

**Rate limiting:**
- 5,000 points per hour (authenticated)
- Each query costs between 1 and ~5,000+ points
- Cost = number of nodes requested, with nested connections multiplying
- Use `rateLimit` field to check: `{ rateLimit { limit cost remaining resetAt } }`

**Pagination pattern (Relay connections):**
```graphql
query($cursor: String) {
  repository(owner: "owner", name: "repo") {
    issues(first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes { title }
    }
  }
}
```

**Node interface:** Fetch any object by global ID: `node(id: "MDQ6...") { ... on Repository { name } }`

## Neon Postgres 18 + pg_graphql

**Setup:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_graphql CASCADE;
```

**Query via SQL:**
```sql
SELECT graphql.resolve($$
  {
    "query": "{ usersCollection(first: 10) { edges { node { id name } } } }"
  }
$$);
```

**Collection naming:** Table `users` becomes `usersCollection`. Access rows via Relay connection pattern: `edges[].node`.

**Filtering:**
```graphql
{
  usersCollection(filter: { name: { eq: "Alice" } }, first: 10) {
    edges { node { id name email } }
  }
}
```

**Mutations:**
```graphql
mutation {
  insertIntoUsersCollection(objects: [{ name: "Bob", email: "bob@example.com" }]) {
    records { id name }
  }
}
```

**Connection string format for Neon:**
```
postgresql://{user}:{password}@{endpoint}.{region}.aws.neon.tech/{dbname}?sslmode=require
```

SSL is mandatory. The endpoint ID is in the hostname (e.g., `ep-cool-dawn-123456`).

## Graphweaver

**Config (graphweaver.config.ts):**
```typescript
export const config = {
  backend: {
    providers: [
      new PostgresProvider({ connectionString: "postgresql://..." }),
      new RestProvider({ baseUrl: "https://api.example.com" }),
    ],
  },
};
```

**Entity definition:**
```typescript
@Entity("User", { provider: "postgres" })
export class User {
  @Field(() => ID) id!: string;
  @Field(() => String) name!: string;
  @RelationshipField(() => [Post], { relatedField: "author" }) posts!: Post[];
}
```

## Strawberry GraphQL (Python)

**Define types and schema:**
```python
import strawberry

@strawberry.type
class User:
    id: strawberry.ID
    name: str
    email: str | None = None

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: strawberry.ID) -> User:
        return User(id=id, name="Alice")

schema = strawberry.Schema(query=Query)
```

**Run with ASGI:**
```python
from strawberry.asgi import GraphQL
app = GraphQL(schema)
```

## gqlgen (Go)

**Config (gqlgen.yml):**
```yaml
schema:
  - graph/*.graphqls
exec:
  filename: graph/generated.go
  package: graph
model:
  filename: graph/model/models_gen.go
  package: model
resolver:
  filename: graph/resolver.go
  type: Resolver
```

**Generate code:** `go run github.com/99designs/gqlgen generate`

## GraphQL Inspector

**Common commands (via npx):**
```bash
npx @graphql-inspector/cli diff old.graphql new.graphql
npx @graphql-inspector/cli validate queries/ schema.graphql
npx @graphql-inspector/cli coverage queries/ schema.graphql
npx @graphql-inspector/cli introspect https://api.example.com/graphql --write schema.graphql
```
