/**
 * Base adapter interface for social media video uploads.
 *
 * Each platform adapter implements this interface to provide
 * a consistent upload API across TikTok, YouTube, and Instagram.
 */

import type {
  DistributionResult,
  Platform,
  PlatformCredentials,
  VideoAsset,
} from "../types.js";

export interface SocialAdapter {
  /** The platform this adapter handles. */
  readonly platform: Platform;

  /**
   * Upload a video asset to the platform.
   *
   * @param asset - The video asset with metadata
   * @param credentials - OAuth credentials for the platform
   * @returns Distribution result with platform-specific IDs
   */
  upload(
    asset: VideoAsset,
    credentials: PlatformCredentials
  ): Promise<DistributionResult>;

  /**
   * Check the status of a previously uploaded video.
   *
   * @param platformVideoId - The platform-specific video ID
   * @param credentials - OAuth credentials for the platform
   * @returns Current status of the upload
   */
  checkStatus(
    platformVideoId: string,
    credentials: PlatformCredentials
  ): Promise<DistributionResult>;
}

/**
 * Helper to build a successful distribution result.
 */
export function successResult(
  platform: Platform,
  platformVideoId: string,
  platformUrl: string
): DistributionResult {
  return {
    platform,
    success: true,
    platformVideoId,
    platformUrl,
  };
}

/**
 * Helper to build a failed distribution result.
 */
export function failureResult(
  platform: Platform,
  error: string
): DistributionResult {
  return {
    platform,
    success: false,
    error,
  };
}
