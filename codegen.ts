import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: "schema/video_pipeline.graphql",
  documents: ["src/social/**/*.ts"],
  generates: {
    "src/social/__generated__/graphql.ts": {
      plugins: [
        "typescript",
        "typescript-operations",
      ],
    },
  },
  ignoreNoDocuments: true,
};

export default config;
