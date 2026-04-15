/**
 * Social media adapter exports.
 *
 * Usage:
 *   import { TikTokAdapter, YouTubeAdapter, InstagramAdapter, createAdapter } from "./adapters/index.js";
 */

export { type SocialAdapter } from "./base.js";
export { TikTokAdapter } from "./tiktok.js";
export { YouTubeAdapter } from "./youtube.js";
export { InstagramAdapter } from "./instagram.js";

import type { Platform } from "../types.js";
import type { SocialAdapter } from "./base.js";
import { TikTokAdapter } from "./tiktok.js";
import { YouTubeAdapter } from "./youtube.js";
import { InstagramAdapter } from "./instagram.js";

/**
 * Factory to create a platform adapter by name.
 *
 * @param platform - Target platform
 * @param igUserId - Required for Instagram; the Business/Creator user ID
 */
export function createAdapter(platform: Platform, igUserId?: string): SocialAdapter {
  switch (platform) {
    case "tiktok":
      return new TikTokAdapter();
    case "youtube_shorts":
      return new YouTubeAdapter();
    case "instagram_reels":
      if (!igUserId) {
        throw new Error("Instagram adapter requires igUserId");
      }
      return new InstagramAdapter(igUserId);
    default: {
      const _exhaustive: never = platform;
      throw new Error(`Unknown platform: ${_exhaustive}`);
    }
  }
}
