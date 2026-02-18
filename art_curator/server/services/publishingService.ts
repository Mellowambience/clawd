import { getScheduledPostsForPublishing, updateScheduledPostStatus, createPostHistory, getArtVariantsByPieceId, getSocialAccountById } from "../db";
import { MetaApiService } from "./metaApiService";

/**
 * Publishing Service
 * Handles publishing scheduled posts to social media platforms
 */
export class PublishingService {
  constructor() {}

  /**
   * Process all scheduled posts that are ready to publish
   */
  async processScheduledPosts(): Promise<void> {
    try {
      const scheduledPosts = await getScheduledPostsForPublishing();

      for (const post of scheduledPosts) {
        await this.publishPost(post);
      }
    } catch (error) {
      console.error("[PublishingService] Error processing scheduled posts:", error);
    }
  }

  /**
   * Publish a single scheduled post
   */
  private async publishPost(post: any): Promise<void> {
    try {
      const platforms = JSON.parse(post.platforms);
      const socialAccount = await getSocialAccountById(post.socialAccountId);

      if (!socialAccount) {
        throw new Error(`Social account ${post.socialAccountId} not found`);
      }

      // Get art variants if art piece is specified
      let imageUrls: string[] = [];
      if (post.artPieceId) {
        const variants = await getArtVariantsByPieceId(post.artPieceId);
        // Get the best variant for each platform
        imageUrls = variants
          .filter((v) => v.variantType.includes("compressed") || v.variantType === "original")
          .map((v) => v.imageUrl);
      }

      // Publish to each platform
      for (const platform of platforms) {
        try {
          let platformPostId: string;

          if (platform === "instagram" && socialAccount.platform === "instagram") {
            platformPostId = await this.publishToInstagram(
              socialAccount.accountId,
              socialAccount.accessToken,
              imageUrls[0] || "",
              post.caption
            );
          } else if (platform === "facebook" && socialAccount.platform === "facebook") {
            platformPostId = await this.publishToFacebook(
              socialAccount.accountId,
              socialAccount.accessToken,
              imageUrls[0] || "",
              post.caption
            );
          } else {
            throw new Error(`Platform ${platform} not configured for account`);
          }

          // Record in post history
          await createPostHistory({
            scheduledPostId: post.id,
            userId: post.userId,
            platform: platform as any,
            platformPostId,
            artPieceId: post.artPieceId,
            caption: post.caption,
            hashtags: post.hashtags,
            status: "published",
            publishedAt: new Date(),
          });
        } catch (platformError) {
          console.error(`[PublishingService] Failed to publish to ${platform}:`, platformError);
          // Continue with other platforms
        }
      }

      // Update scheduled post status
      await updateScheduledPostStatus(post.id, "published", undefined);
    } catch (error) {
      console.error("[PublishingService] Error publishing post:", error);
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      await updateScheduledPostStatus(post.id, "failed", errorMessage);
    }
  }

  /**
   * Publish to Instagram
   */
  private async publishToInstagram(
    igUserId: string,
    accessToken: string,
    imageUrl: string,
    caption: string
  ): Promise<string> {
    try {
      const metaApiService = new MetaApiService(accessToken);
      return await metaApiService.postToInstagram(igUserId, imageUrl, caption);
    } catch (error) {
      console.error("[PublishingService] Instagram publishing failed:", error);
      throw error;
    }
  }

  /**
   * Publish to Facebook
   */
  private async publishToFacebook(
    pageId: string,
    accessToken: string,
    imageUrl: string,
    caption: string
  ): Promise<string> {
    try {
      const metaApiService = new MetaApiService(accessToken);
      return await metaApiService.postToFacebookPage(pageId, imageUrl, caption);
    } catch (error) {
      console.error("[PublishingService] Facebook publishing failed:", error);
      throw error;
    }
  }
}

/**
 * Factory function to create publishing service
 */
export function createPublishingService(): PublishingService {
  return new PublishingService();
}
