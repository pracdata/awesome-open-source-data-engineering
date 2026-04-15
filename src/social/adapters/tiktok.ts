/**
 * TikTok Video Upload API adapter.
 *
 * Uses the TikTok Content Posting API v2 for video uploads.
 * Requires an access_token obtained via TikTok Login Kit OAuth.
 *
 * Flow:
 *   1. POST /v2/post/publish/video/init/ — initialize upload
 *   2. PUT to upload_url — chunked video upload
 *   3. POST /v2/post/publish/status/fetch/ — poll until published
 *
 * @see https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
 */

import { TikTokUploadConfig, type PlatformCredentials, type VideoAsset, type DistributionResult } from "../types.js";
import { type SocialAdapter, successResult, failureResult } from "./base.js";

const TIKTOK_API_BASE = "https://open.tiktokapis.com";

interface TikTokInitResponse {
  data: {
    publish_id: string;
    upload_url: string;
  };
  error: {
    code: string;
    message: string;
  };
}

interface TikTokStatusResponse {
  data: {
    status: "PROCESSING_UPLOAD" | "PROCESSING_DOWNLOAD" | "PUBLISH_COMPLETE" | "FAILED";
    publish_id: string;
    video_id?: string;
  };
  error: {
    code: string;
    message: string;
  };
}

export class TikTokAdapter implements SocialAdapter {
  readonly platform = "tiktok" as const;

  private config: TikTokUploadConfig;

  constructor(config?: Partial<TikTokUploadConfig>) {
    this.config = TikTokUploadConfig.parse(config ?? {});
  }

  async upload(asset: VideoAsset, credentials: PlatformCredentials): Promise<DistributionResult> {
    if (!asset.url) {
      return failureResult("tiktok", "Video asset has no URL");
    }

    try {
      // Step 1: Initialize the upload
      const initResponse = await fetch(`${TIKTOK_API_BASE}/v2/post/publish/video/init/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${credentials.accessToken}`,
          "Content-Type": "application/json; charset=UTF-8",
        },
        body: JSON.stringify({
          post_info: {
            title: asset.metadata.title,
            description: asset.metadata.description ?? "",
            privacy_level: this.config.privacyLevel,
            disable_duet: this.config.disableDuet,
            disable_stitch: this.config.disableStitch,
            disable_comment: this.config.disableComment,
            brand_content_toggle: this.config.brandContentToggle,
            brand_organic_toggle: this.config.brandOrganicToggle,
          },
          source_info: {
            source: "PULL_FROM_URL",
            video_url: asset.url,
          },
        }),
      });

      const initData = (await initResponse.json()) as TikTokInitResponse;

      if (initData.error?.code !== "ok") {
        return failureResult("tiktok", `Init failed: ${initData.error.message}`);
      }

      const publishId = initData.data.publish_id;

      // Step 2: Poll for completion
      return await this.pollStatus(publishId, credentials);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return failureResult("tiktok", `Upload error: ${message}`);
    }
  }

  async checkStatus(platformVideoId: string, credentials: PlatformCredentials): Promise<DistributionResult> {
    return this.pollStatus(platformVideoId, credentials);
  }

  private async pollStatus(
    publishId: string,
    credentials: PlatformCredentials,
    maxAttempts = 30,
    intervalMs = 5000
  ): Promise<DistributionResult> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const statusResponse = await fetch(`${TIKTOK_API_BASE}/v2/post/publish/status/fetch/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${credentials.accessToken}`,
          "Content-Type": "application/json; charset=UTF-8",
        },
        body: JSON.stringify({ publish_id: publishId }),
      });

      const statusData = (await statusResponse.json()) as TikTokStatusResponse;

      if (statusData.data.status === "PUBLISH_COMPLETE") {
        const videoId = statusData.data.video_id ?? publishId;
        return successResult("tiktok", videoId, `https://www.tiktok.com/@/video/${videoId}`);
      }

      if (statusData.data.status === "FAILED") {
        return failureResult("tiktok", `Publish failed: ${statusData.error.message}`);
      }

      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }

    return failureResult("tiktok", "Upload timed out waiting for publish");
  }
}
