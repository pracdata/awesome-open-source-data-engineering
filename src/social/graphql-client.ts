/**
 * GraphQL Client for the Python Generation Core
 *
 * Communicates with the Strawberry GraphQL server to trigger video
 * generation and retrieve results. Uses fetch + Zod for type-safe responses.
 */

import {
  type GenerationTask,
  GenerationTask as GenerationTaskSchema,
  type DistributionTask,
  DistributionTask as DistributionTaskSchema,
  type GenerateVideoInput,
  type DistributeVideoInput,
  type CinematicPromptInput,
} from "./types.js";

const DEFAULT_ENDPOINT = "http://localhost:8000/graphql";

interface GraphQLResponse<T> {
  data?: T;
  errors?: Array<{ message: string; path?: string[] }>;
}

export class VideoPipelineClient {
  private endpoint: string;

  constructor(endpoint: string = DEFAULT_ENDPOINT) {
    this.endpoint = endpoint;
  }

  private async query<T>(
    queryStr: string,
    variables?: Record<string, unknown>
  ): Promise<T> {
    const response = await fetch(this.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: queryStr, variables }),
    });

    if (!response.ok) {
      throw new Error(
        `GraphQL request failed: ${response.status} ${response.statusText}`
      );
    }

    const result = (await response.json()) as GraphQLResponse<T>;

    if (result.errors?.length) {
      throw new Error(
        `GraphQL errors: ${result.errors.map((e) => e.message).join(", ")}`
      );
    }

    if (!result.data) {
      throw new Error("No data returned from GraphQL server");
    }

    return result.data;
  }

  // ── Mutations ───────────────────────────────────────────────

  async generateVideo(input: GenerateVideoInput): Promise<GenerationTask> {
    const data = await this.query<{ generateVideo: unknown }>(
      `mutation GenerateVideo($input: GenerateVideoInput!) {
        generateVideo(input: $input) {
          id prompt model resolution durationSeconds status error createdAt
          videoAsset {
            id url status platforms createdAt updatedAt
            metadata { title description resolution durationSeconds hasAudio tags }
          }
        }
      }`,
      { input }
    );
    return GenerationTaskSchema.parse(data.generateVideo);
  }

  async generateCinematicPrompt(input: CinematicPromptInput): Promise<string> {
    const data = await this.query<{ generateCinematicPrompt: string }>(
      `mutation GenerateCinematicPrompt($input: CinematicPromptInput!) {
        generateCinematicPrompt(input: $input)
      }`,
      { input }
    );
    return data.generateCinematicPrompt;
  }

  async distributeVideo(
    input: DistributeVideoInput
  ): Promise<DistributionTask> {
    const data = await this.query<{ distributeVideo: unknown }>(
      `mutation DistributeVideo($input: DistributeVideoInput!) {
        distributeVideo(input: $input) {
          id videoAssetId platforms createdAt
          results { platform success platformVideoId platformUrl error }
        }
      }`,
      { input }
    );
    return DistributionTaskSchema.parse(data.distributeVideo);
  }

  async retryGeneration(taskId: string): Promise<GenerationTask> {
    const data = await this.query<{ retryGeneration: unknown }>(
      `mutation RetryGeneration($taskId: ID!) {
        retryGeneration(taskId: $taskId) {
          id prompt model resolution durationSeconds status error createdAt
          videoAsset {
            id url status platforms createdAt updatedAt
            metadata { title description resolution durationSeconds hasAudio tags }
          }
        }
      }`,
      { taskId }
    );
    return GenerationTaskSchema.parse(data.retryGeneration);
  }

  // ── Queries ─────────────────────────────────────────────────

  async getGenerationTask(id: string): Promise<GenerationTask | null> {
    const data = await this.query<{ generationTask: unknown | null }>(
      `query GetGenerationTask($id: ID!) {
        generationTask(id: $id) {
          id prompt model resolution durationSeconds status error createdAt
          videoAsset {
            id url status platforms createdAt updatedAt
            metadata { title description resolution durationSeconds hasAudio tags }
          }
        }
      }`,
      { id }
    );
    return data.generationTask
      ? GenerationTaskSchema.parse(data.generationTask)
      : null;
  }

  async listGenerationTasks(
    status?: string,
    limit = 20
  ): Promise<GenerationTask[]> {
    const data = await this.query<{ listGenerationTasks: unknown[] }>(
      `query ListGenerationTasks($status: String, $limit: Int) {
        listGenerationTasks(status: $status, limit: $limit) {
          id prompt model resolution durationSeconds status error createdAt
          videoAsset {
            id url status platforms createdAt updatedAt
            metadata { title description resolution durationSeconds hasAudio tags }
          }
        }
      }`,
      { status, limit }
    );
    return data.listGenerationTasks.map((t) => GenerationTaskSchema.parse(t));
  }
}
