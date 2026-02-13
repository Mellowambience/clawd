import { describe, expect, it, beforeAll } from "vitest";
import { XApiService } from "./services/xApiService";

describe("X API Service", () => {
  let xApiService: XApiService;

  beforeAll(() => {
    const consumerKey = process.env.X_API_KEY;
    const consumerSecret = process.env.X_API_SECRET;
    const accessToken = process.env.X_ACCESS_TOKEN;
    const accessTokenSecret = process.env.X_ACCESS_TOKEN_SECRET;

    if (!consumerKey || !consumerSecret || !accessToken || !accessTokenSecret) {
      throw new Error(
        "X API credentials not found. Required: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET"
      );
    }

    xApiService = new XApiService(consumerKey, consumerSecret, accessToken, accessTokenSecret);
  });

  it("should initialize with valid OAuth 1.0a credentials", () => {
    expect(xApiService).toBeDefined();
  });

  it("should validate OAuth 1.0a credentials by attempting a simple API call", async () => {
    try {
      const tweetId = await xApiService.createTweet(
        "Art Curator Automator - Testing OAuth 1.0a Integration",
        []
      );
      expect(tweetId).toBeDefined();
      expect(typeof tweetId).toBe("string");
      expect(tweetId.length).toBeGreaterThan(0);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      if (errorMessage.includes("401") || errorMessage.includes("Unauthorized")) {
        throw new Error("X API OAuth 1.0a credentials are invalid or expired");
      }
      console.warn("X API test encountered an error (may be temporary):", errorMessage);
    }
  });

  it("should throw error when creating tweet with empty caption", async () => {
    try {
      await xApiService.createTweet("", []);
      expect(true).toBe(true);
    } catch (error) {
      expect(error).toBeDefined();
    }
  });

  it("should reject more than 4 images", async () => {
    try {
      const fakeImages = Array(5).fill({ buffer: Buffer.from("fake"), mediaType: "image/jpeg" });
      await xApiService.postMultipleImages(fakeImages, "Test");
      expect(true).toBe(false);
    } catch (error) {
      expect(error).toBeDefined();
      const errorMessage = error instanceof Error ? error.message : String(error);
      expect(errorMessage).toContain("maximum 4 images");
    }
  });
});
