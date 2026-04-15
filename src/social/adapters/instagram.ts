/**
 * Instagram Reels adapter using the Meta Graph API.
 *
 * Requires a Business or Creator account connected via Meta Business Suite.
 * Uses the Reels Publishing API:
 *   1. POST /{ig-user-id}/media — create container with video_url
 *   2. GET /{container-id}?fields=status_code — poll until FINISHED
 *   3. POST /{ig-user-id}/media_publish — publish the container
 *
 * @see https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/content-publishing
 */

import {
  InstagramReelsConfig,
  type PlatformCredentials,
  type VideoAsset,
  type DistributionResult,
} from "../types.js";
import { type SocialAdapter, successResult, failureResult } from "./base.js";

const GRAPH_API_BASE = "https://graph.instagram.com/v21.0";

interface IGMediaResponse {
  id: string;
}

interface IGStatusResponse {
  status_code: "EXPIRED" | "ERROR" | "FINISHED" | "IN_PROGRESS" | "PUBLISHED";
  id: string;
}

interface IGPublishResponse {
  id: string;
}

export class InstagramAdapter implements SocialAdapter {
  readonly platform = "instagram_reels" as const;

  private config: InstagramReelsConfig;
  private igUserId: string;

  /**
   * @param igUserId - The Instagram Business/Creator user ID
   * @param config - Reels-specific configuration
   */
  constructor(igUserId: string, config?: Partial<InstagramReelsConfig>) {
    this.igUserId = igUserId;
    this.config = InstagramReelsConfig.parse(config ?? {});
  }

  async upload(asset: VideoAsset, credentials: PlatformCredentials): Promise<DistributionResult> {
    if (!asset.url) {
      return failureResult("instagram_reels", "Video asset has no URL");
    }

    try {
      // Step 1: Create media container
      const caption = this.buildCaption(asset);

      const containerParams = new URLSearchParams({
        media_type: "REELS",
        video_url: asset.url,
        caption,
        share_to_feed: String(this.config.shareToFeed),
        access_token: credentials.accessToken,
      });

      if (this.config.locationId) {
        containerParams.set("location_id", this.config.locationId);
      }

      if (this.config.collaborators.length > 0) {
        containerParams.set("collaborators", JSON.stringify(this.config.collaborators));
      }

      const containerResponse = await fetch(`${GRAPH_API_BASE}/${this.igUserId}/media`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: containerParams.toString(),
      });

      if (!containerResponse.ok) {
        const errorText = await containerResponse.text();
        return failureResult("instagram_reels", `Container creation failed: ${errorText}`);
      }

      const containerData = (await containerResponse.json()) as IGMediaResponse;
      const containerId = containerData.id;

      // Step 2: Poll until container is ready
      const ready = await this.waitForContainer(containerId, credentials);
      if (!ready) {
        return failureResult("instagram_reels", "Container processing timed out or failed");
      }

      // Step 3: Publish the container
      const publishResponse = await fetch(`${GRAPH_API_BASE}/${this.igUserId}/media_publish`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          creation_id: containerId,
          access_token: credentials.accessToken,
        }).toString(),
      });

      if (!publishResponse.ok) {
        const errorText = await publishResponse.text();
        return failureResult("instagram_reels", `Publish failed: ${errorText}`);
      }

      const publishData = (await publishResponse.json()) as IGPublishResponse;

      return successResult(
        "instagram_reels",
        publishData.id,
        `https://www.instagram.com/reel/${publishData.id}/`
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return failureResult("instagram_reels", `Upload error: ${message}`);
    }
  }

  async checkStatus(platformVideoId: string, credentials: PlatformCredentials): Promise<DistributionResult> {
    try {
      const response = await fetch(
        `${GRAPH_API_BASE}/${platformVideoId}?fields=id,media_url,permalink&access_token=${credentials.accessToken}`
      );

      if (!response.ok) {
        return failureResult("instagram_reels", `Status check failed: ${response.statusText}`);
      }

      const data = (await response.json()) as IGPublishResponse & { permalink?: string };

      return successResult(
        "instagram_reels",
        data.id,
        data.permalink ?? `https://www.instagram.com/reel/${data.id}/`
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return failureResult("instagram_reels", `Status check error: ${message}`);
    }
  }

  private buildCaption(asset: VideoAsset): string {
    const parts: string[] = [];

    if (asset.metadata.description) {
      parts.push(asset.metadata.description);
    }

    if (asset.metadata.tags.length > 0) {
      const hashtags = asset.metadata.tags.map((t) => (t.startsWith("#") ? t : `#${t}`)).join(" ");
      parts.push(hashtags);
    }

    const caption = parts.join("\n\n");
    return caption.slice(0, this.config.captionMaxLength);
  }

  private async waitForContainer(
    containerId: string,
    credentials: PlatformCredentials,
    maxAttempts = 60,
    intervalMs = 5000
  ): Promise<boolean> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const response = await fetch(
        `${GRAPH_API_BASE}/${containerId}?fields=status_code&access_token=${credentials.accessToken}`
      );

      if (!response.ok) {
        return false;
      }

      const data = (await response.json()) as IGStatusResponse;

      if (data.status_code === "FINISHED") {
        return true;
      }

      if (data.status_code === "ERROR" || data.status_code === "EXPIRED") {
        return false;
      }

      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }

    return false;
  }
}
