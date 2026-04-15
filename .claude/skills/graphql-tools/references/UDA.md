# Netflix UDA (Unified Data Architecture) Reference

Netflix's Unified Data Architecture bridges multiple data representations
(GraphQL, Avro, RDF/Turtle) into a coherent schema model. This skill
incorporates UDA patterns for embedding-aware schema management.

Source: https://github.com/Netflix-Skunkworks/uda

## Core Concept

UDA provides a single data model expressed across multiple serialization formats:
- **GraphQL** (.graphqls) -- API-facing schema with typed fields and relationships
- **Avro** (.avro) -- Binary serialization for data pipelines and streaming
- **RDF/Turtle** (.ttl) -- Semantic web representation for knowledge graphs

All three representations describe the same entities, enabling interoperability
across API, streaming, and graph-based systems.

## UDA Directives

The key UDA extension is the `@udaUri` directive, which maps GraphQL types
and fields to RDF ontology URIs:

```graphql
type ONEPIECE_Character
    @key(fields: "onepiece_rname")
    @udaUri(uri: "https://rdf.netflix.net/onto/onepiece#Character") {

  onepiece_ename: String
      @udaUri(uri: "https://rdf.netflix.net/onto/onepiece#ename")

  onepiece_devilFruit: ONEPIECE_DevilFruit
      @udaUri(uri: "https://rdf.netflix.net/onto/onepiece#devilFruit")

  onepiece_rname: String!
      @udaUri(uri: "https://rdf.netflix.net/onto/onepiece#rname")
}
```

This enables:
1. **GraphQL <-> RDF mapping**: Every type/field has a corresponding ontology URI
2. **Federation compatibility**: `@key` directives work with Apollo Federation
3. **Schema-as-knowledge-graph**: GraphQL schemas become queryable via SPARQL

## Included Example Files

Located in `assets/uda-intro-blog/`:

| File | Format | Content |
|---|---|---|
| `onepiece.graphqls` | GraphQL SDL | Character and DevilFruit types with `@udaUri` directives |
| `onepiece.avro` | Avro schema | Same entities in Avro binary serialization format |
| `onepiece.ttl` | RDF/Turtle | Ontology definition with classes and properties |
| `onepiece_character_data_container.ttl` | RDF/Turtle | Character instance data as RDF triples |
| `onepiece_character_mappings.ttl` | RDF/Turtle | Mapping rules between GraphQL and RDF |

## Embedding UDA Schemas

Use `embed_tools.py --embed-uda` to generate vector embeddings for all UDA
schema files and store them in the Neon pgvector `uda_schema_registry` table.
This enables semantic search across schema representations:

```bash
# Embed all UDA schemas
uv run scripts/embed_tools.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" --embed-uda

# Search for related schemas
uv run scripts/tool_search.py --database-url "$DATABASE_URL" --hf-token "$HF_TOKEN" \
    --query "character entity with relationships" --search-uda
```

## Applying UDA Patterns

When building a new data model, UDA patterns help maintain consistency:

1. **Start with GraphQL** -- Define types with `@key` and `@udaUri` directives
2. **Generate Avro** -- Map GraphQL types to Avro records for streaming pipelines
3. **Generate RDF** -- Map types to ontology classes for knowledge graph queries
4. **Embed all three** -- Store in pgvector for semantic discovery across formats

The `uda_schema_registry` table stores all three formats with embeddings,
enabling cross-format schema search:

```sql
-- Find schemas semantically similar to a query
SELECT schema_name, schema_type, 1 - (embedding <=> query_vec) AS similarity
FROM uda_schema_registry
WHERE 1 - (embedding <=> query_vec) > 0.4
ORDER BY embedding <=> query_vec
LIMIT 5;
```
