/**
 * Meta API Service for Instagram and Facebook
 * Handles image posting to both Instagram and Facebook
 */
export class MetaApiService {
  private apiVersion = "v24.0";
  private graphApiBaseUrl = "https://graph.instagram.com";
  private facebookGraphApiBaseUrl = "https://graph.facebook.com";

  constructor(private accessToken: string) {
    if (!accessToken) {
      throw new Error("Meta access token is required");
    }
  }

  /**
   * Create a container for Instagram media (step 1 of 2-step process)
   */
  async createInstagramContainer(
    igUserId: string,
    imageUrl: string,
    caption: string,
    mediaType: "IMAGE" | "CAROUSEL" = "IMAGE"
  ): Promise<string> {
    try {
      const payload: Record<string, any> = {
        image_url: imageUrl,
        caption,
        media_type: mediaType,
        access_token: this.accessToken,
      };

      const response = await fetch(`${this.graphApiBaseUrl}/${this.apiVersion}/${igUserId}/media`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Meta API error: ${response.status} - ${error}`);
      }

      const data = (await response.json()) as { id: string };
      return data.id;
    } catch (error) {
      console.error("[MetaApiService] Instagram container creation failed:", error);
      throw error;
    }
  }

  /**
   * Publish an Instagram container (step 2 of 2-step process)
   */
  async publishInstagramContainer(containerId: string): Promise<string> {
    try {
      const payload = {
        access_token: this.accessToken,
      };

      const response = await fetch(
        `${this.graphApiBaseUrl}/${this.apiVersion}/${containerId}/publish`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Meta API error: ${response.status} - ${error}`);
      }

      const data = (await response.json()) as { id: string };
      return data.id;
    } catch (error) {
      console.error("[MetaApiService] Instagram container publishing failed:", error);
      throw error;
    }
  }

  /**
   * Post an image to Instagram (complete flow)
   */
  async postToInstagram(
    igUserId: string,
    imageUrl: string,
    caption: string
  ): Promise<string> {
    try {
      // Step 1: Create container
      const containerId = await this.createInstagramContainer(
        igUserId,
        imageUrl,
        caption,
        "IMAGE"
      );

      // Step 2: Publish container
      const mediaId = await this.publishInstagramContainer(containerId);

      return mediaId;
    } catch (error) {
      console.error("[MetaApiService] Instagram post failed:", error);
      throw error;
    }
  }

  /**
   * Post a photo to Facebook page
   */
  async postToFacebookPage(
    pageId: string,
    imageUrl: string,
    caption: string
  ): Promise<string> {
    try {
      const payload = {
        url: imageUrl,
        caption,
        access_token: this.accessToken,
      };

      const response = await fetch(
        `${this.facebookGraphApiBaseUrl}/${this.apiVersion}/${pageId}/photos`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Meta API error: ${response.status} - ${error}`);
      }

      const data = (await response.json()) as { id: string };
      return data.id;
    } catch (error) {
      console.error("[MetaApiService] Facebook post failed:", error);
      throw error;
    }
  }

  /**
   * Create a carousel container for Instagram (multiple images)
   */
  async createInstagramCarousel(
    igUserId: string,
    imageUrls: string[],
    caption: string
  ): Promise<string> {
    try {
      if (imageUrls.length < 2 || imageUrls.length > 10) {
        throw new Error("Carousel must have between 2 and 10 images");
      }

      // Create individual containers for each image
      const childIds: string[] = [];
      for (const imageUrl of imageUrls) {
        const childId = await this.createInstagramContainer(
          igUserId,
          imageUrl,
          "",
          "IMAGE"
        );
        childIds.push(childId);
      }

      // Create parent carousel container
      const payload = {
        media_type: "CAROUSEL",
        children: childIds,
        caption,
        access_token: this.accessToken,
      };

      const response = await fetch(
        `${this.graphApiBaseUrl}/${this.apiVersion}/${igUserId}/media`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Meta API error: ${response.status} - ${error}`);
      }

      const data = (await response.json()) as { id: string };
      return data.id;
    } catch (error) {
      console.error("[MetaApiService] Instagram carousel creation failed:", error);
      throw error;
    }
  }

  /**
   * Get Instagram business account info
   */
  async getInstagramBusinessAccount(igUserId: string): Promise<any> {
    try {
      const response = await fetch(
        `${this.graphApiBaseUrl}/${this.apiVersion}/${igUserId}?fields=id,username,name,biography,profile_picture_url&access_token=${this.accessToken}`
      );

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Meta API error: ${response.status} - ${error}`);
      }

      return await response.json();
    } catch (error) {
      console.error("[MetaApiService] Get account info failed:", error);
      throw error;
    }
  }

  /**
   * Get Facebook page info
   */
  async getFacebookPageInfo(pageId: string): Promise<any> {
    try {
      const response = await fetch(
        `${this.facebookGraphApiBaseUrl}/${this.apiVersion}/${pageId}?fields=id,name,picture&access_token=${this.accessToken}`
      );

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Meta API error: ${response.status} - ${error}`);
      }

      return await response.json();
    } catch (error) {
      console.error("[MetaApiService] Get page info failed:", error);
      throw error;
    }
  }
}

/**
 * Factory function to create Meta API service
 */
export function createMetaApiService(accessToken: string): MetaApiService {
  if (!accessToken) {
    throw new Error("Meta access token is required");
  }
  return new MetaApiService(accessToken);
}

export type MetaApiServiceType = MetaApiService;
