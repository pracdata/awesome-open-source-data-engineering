/**
 * YouTube Data API v3 adapter for Shorts uploads.
 *
 * Uses the Videos: insert endpoint with multipart upload.
 * Videos are automatically treated as Shorts when:
 *   - Duration is <= 60 seconds
 *   - Aspect ratio is 9:16 (vertical)
 *   - Title or description includes #Shorts
 *
 * @see https://developers.google.com/youtube/v3/docs/videos/insert
 */

import { YouTubeUploadConfig, type PlatformCredentials, type VideoAsset, type DistributionResult } from "../types.js";
import { type SocialAdapter, successResult, failureResult } from "./base.js";

const YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos";
const YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos";

interface YouTubeVideoResponse {
  id: string;
  snippet: {
    title: string;
    publishedAt: string;
  };
  status: {
    uploadStatus: "uploaded" | "processed" | "failed" | "rejected" | "deleted";
    privacyStatus: string;
  };
}

export class YouTubeAdapter implements SocialAdapter {
  readonly platform = "youtube_shorts" as const;

  private config: YouTubeUploadConfig;

  constructor(config?: Partial<YouTubeUploadConfig>) {
    this.config = YouTubeUploadConfig.parse(config ?? {});
  }

  async upload(asset: VideoAsset, credentials: PlatformCredentials): Promise<DistributionResult> {
    if (!asset.url) {
      return failureResult("youtube_shorts", "Video asset has no URL");
    }

    try {
      // Ensure #Shorts is in the description for Shorts classification
      const description = this.config.shorts
        ? `${asset.metadata.description ?? ""}\n\n#Shorts`.trim()
        : (asset.metadata.description ?? "");

      // Build the video resource metadata
      const videoResource = {
        snippet: {
          title: asset.metadata.title,
          description,
          tags: asset.metadata.tags,
          categoryId: this.config.categoryId,
        },
        status: {
          privacyStatus: this.config.privacyStatus,
          selfDeclaredMadeForKids: this.config.madeForKids,
        },
      };

      // Fetch the video file
      const videoResponse = await fetch(asset.url);
      if (!videoResponse.ok) {
        return failureResult("youtube_shorts", `Failed to fetch video: ${videoResponse.statusText}`);
      }
      const videoBlob = await videoResponse.blob();

      // Step 1: Initiate resumable upload
      const initResponse = await fetch(
        `${YOUTUBE_UPLOAD_URL}?uploadType=resumable&part=snippet,status`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${credentials.accessToken}`,
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": String(videoBlob.size),
            "X-Upload-Content-Type": "video/mp4",
          },
          body: JSON.stringify(videoResource),
        }
      );

      if (!initResponse.ok) {
        const errorText = await initResponse.text();
        return failureResult("youtube_shorts", `Upload init failed: ${errorText}`);
      }

      const uploadUrl = initResponse.headers.get("Location");
      if (!uploadUrl) {
        return failureResult("youtube_shorts", "No upload URL returned from YouTube");
      }

      // Step 2: Upload the video data
      const uploadResponse = await fetch(uploadUrl, {
        method: "PUT",
        headers: {
          "Content-Type": "video/mp4",
          "Content-Length": String(videoBlob.size),
        },
        body: videoBlob,
      });

      if (!uploadResponse.ok) {
        const errorText = await uploadResponse.text();
        return failureResult("youtube_shorts", `Video upload failed: ${errorText}`);
      }

      const result = (await uploadResponse.json()) as YouTubeVideoResponse;

      return successResult(
        "youtube_shorts",
        result.id,
        `https://youtube.com/shorts/${result.id}`
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return failureResult("youtube_shorts", `Upload error: ${message}`);
    }
  }

  async checkStatus(platformVideoId: string, credentials: PlatformCredentials): Promise<DistributionResult> {
    try {
      const response = await fetch(
        `${YOUTUBE_API_URL}?id=${platformVideoId}&part=status,snippet`,
        {
          headers: {
            Authorization: `Bearer ${credentials.accessToken}`,
          },
        }
      );

      if (!response.ok) {
        return failureResult("youtube_shorts", `Status check failed: ${response.statusText}`);
      }

      const data = (await response.json()) as { items?: YouTubeVideoResponse[] };
      const items = data.items;

      if (!items?.length) {
        return failureResult("youtube_shorts", "Video not found");
      }

      const video = items[0];
      if (video.status.uploadStatus === "processed") {
        return successResult(
          "youtube_shorts",
          video.id,
          `https://youtube.com/shorts/${video.id}`
        );
      }

      if (video.status.uploadStatus === "failed" || video.status.uploadStatus === "rejected") {
        return failureResult("youtube_shorts", `Video ${video.status.uploadStatus}`);
      }

      return {
        platform: "youtube_shorts",
        success: false,
        platformVideoId: video.id,
        error: `Still processing: ${video.status.uploadStatus}`,
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return failureResult("youtube_shorts", `Status check error: ${message}`);
    }
  }
}
