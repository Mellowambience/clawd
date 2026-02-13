// Using native fetch available in Node.js 18+
import { TwitterApi } from "twitter-api-v2";

/**
 * X API Service for posting images and tweets
 * Uses twitter-api-v2 library with OAuth 1.0a User Context
 */
export class XApiService {
  private client: TwitterApi;
  private userClient: any;
  private v1Client: any;

  constructor(
    consumerKey: string,
    consumerSecret: string,
    accessToken: string,
    accessTokenSecret: string
  ) {
    if (!consumerKey || !consumerSecret || !accessToken || !accessTokenSecret) {
      throw new Error("All X API OAuth 1.0a credentials are required");
    }

    this.client = new TwitterApi({
      appKey: consumerKey,
      appSecret: consumerSecret,
      accessToken: accessToken,
      accessSecret: accessTokenSecret,
    });

    this.userClient = this.client.readWrite;
  }

  /**
   * Create a tweet with attached media
   * @param text - Tweet text/caption
   * @param mediaIds - Array of media IDs to attach (max 4)
   * @returns Tweet ID
   */
  async createTweet(text: string, mediaIds: string[]): Promise<string> {
    try {
      if (mediaIds.length > 4) {
        throw new Error("X API allows maximum 4 images per tweet");
      }

      const payload: any = {
        text,
      };

      if (mediaIds.length > 0) {
        payload.media = {
          media_ids: mediaIds,
        };
      }

      const response = await this.userClient.v2.tweet(payload);
      return response.data.id;
    } catch (error) {
      console.error("[XApiService] Tweet creation failed:", error);
      throw error;
    }
  }

  /**
   * Upload media to X
   * @param imageBuffer - Image file buffer
   * @param mediaType - Image type (image/jpeg, image/png, etc.)
   * @returns Media ID for use in tweet creation
   */
  async uploadMedia(imageBuffer: Buffer, mediaType: string): Promise<string> {
    try {
      const response = await this.userClient.v1.uploadMedia(imageBuffer, {
        mimeType: mediaType,
      });
      return response.media_id_string;
    } catch (error) {
      console.error("[XApiService] Media upload failed:", error);
      throw error;
    }
  }

  /**
   * Post an image with caption to X
   * @param imageBuffer - Image file buffer
   * @param mediaType - Media type
   * @param caption - Tweet caption/text
   * @returns Tweet ID
   */
  async postImage(imageBuffer: Buffer, mediaType: string, caption: string): Promise<string> {
    try {
      // Upload media first
      const mediaId = await this.uploadMedia(imageBuffer, mediaType);

      // Create tweet with media
      const tweetId = await this.createTweet(caption, [mediaId]);

      return tweetId;
    } catch (error) {
      console.error("[XApiService] Post image failed:", error);
      throw error;
    }
  }

  /**
   * Post multiple images in a single tweet
   * @param images - Array of {buffer, mediaType}
   * @param caption - Tweet caption
   * @returns Tweet ID
   */
  async postMultipleImages(
    images: Array<{ buffer: Buffer; mediaType: string }>,
    caption: string
  ): Promise<string> {
    try {
      if (images.length > 4) {
        throw new Error("X API allows maximum 4 images per tweet");
      }

      // Upload all media
      const mediaIds: string[] = [];
      for (const image of images) {
        const mediaId = await this.uploadMedia(image.buffer, image.mediaType);
        mediaIds.push(mediaId);
      }

      // Create tweet with all media
      const tweetId = await this.createTweet(caption, mediaIds);

      return tweetId;
    } catch (error) {
      console.error("[XApiService] Post multiple images failed:", error);
      throw error;
    }
  }
}

/**
 * Factory function to create X API service with environment variables
 */
export function createXApiService(): XApiService {
  const consumerKey = process.env.X_API_KEY;
  const consumerSecret = process.env.X_API_SECRET;
  const accessToken = process.env.X_ACCESS_TOKEN;
  const accessTokenSecret = process.env.X_ACCESS_TOKEN_SECRET;

  if (!consumerKey || !consumerSecret || !accessToken || !accessTokenSecret) {
    throw new Error(
      "X API credentials not found. Required: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET"
    );
  }

  return new XApiService(consumerKey, consumerSecret, accessToken, accessTokenSecret);
}

// Re-export types for use in other modules
export type XApiServiceType = XApiService;
