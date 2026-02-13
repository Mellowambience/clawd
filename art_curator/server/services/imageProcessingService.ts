import sharp from "sharp";
import { storagePut } from "../storage";

interface ImageVariant {
  type: string;
  width: number;
  height: number;
  format: "jpeg" | "webp" | "png";
  quality?: number;
}

/**
 * Image Processing Service
 * Handles upscaling, contrast enhancement, compression, and variant generation
 */
export class ImageProcessingService {
  /**
   * Process image with contrast enhancement and sharpening
   */
  async enhanceImage(imageBuffer: Buffer): Promise<Buffer> {
    try {
      return await sharp(imageBuffer)
        .modulate({ saturation: 1.1 })
        .sharpen({ sigma: 1.5 })
        .toBuffer();
    } catch (error) {
      console.error("[ImageProcessingService] Enhancement failed:", error);
      throw error;
    }
  }

  /**
   * Upscale image using bicubic interpolation
   */
  async upscaleImage(imageBuffer: Buffer, scaleFactor: number = 2): Promise<Buffer> {
    try {
      const metadata = await sharp(imageBuffer).metadata();
      if (!metadata.width || !metadata.height) {
        throw new Error("Cannot determine image dimensions");
      }

      const newWidth = Math.round(metadata.width * scaleFactor);
      const newHeight = Math.round(metadata.height * scaleFactor);

      return await sharp(imageBuffer)
        .resize(newWidth, newHeight, {
          kernel: sharp.kernel.cubic,
        })
        .toBuffer();
    } catch (error) {
      console.error("[ImageProcessingService] Upscaling failed:", error);
      throw error;
    }
  }

  /**
   * Generate image variants for different platforms
   */
  async generateVariants(
    imageBuffer: Buffer,
    userId: number,
    artPieceId: number
  ): Promise<Array<{ type: string; url: string; buffer: Buffer }>> {
    try {
      const variants: Array<{ type: string; url: string; buffer: Buffer }> = [];

      // Original (enhanced)
      const enhanced = await this.enhanceImage(imageBuffer);
      const enhancedUrl = await this.uploadToS3(enhanced, userId, artPieceId, "original", "jpeg");
      variants.push({ type: "original", url: enhancedUrl, buffer: enhanced });

      // Upscaled
      const upscaled = await this.upscaleImage(enhanced, 2);
      const upscaledUrl = await this.uploadToS3(upscaled, userId, artPieceId, "upscaled", "jpeg");
      variants.push({ type: "upscaled", url: upscaledUrl, buffer: upscaled });

      // Compressed JPEG
      const compressedJpeg = await sharp(enhanced)
        .jpeg({ quality: 85, progressive: true })
        .toBuffer();
      const jpegUrl = await this.uploadToS3(compressedJpeg, userId, artPieceId, "compressed_jpg", "jpeg");
      variants.push({ type: "compressed_jpg", url: jpegUrl, buffer: compressedJpeg });

      // Compressed WebP
      const compressedWebp = await sharp(enhanced)
        .webp({ quality: 85 })
        .toBuffer();
      const webpUrl = await this.uploadToS3(compressedWebp, userId, artPieceId, "compressed_webp", "webp");
      variants.push({ type: "compressed_webp", url: webpUrl, buffer: compressedWebp });

      // Instagram Portrait (4:5 ratio)
      const instagramPortrait = await this.resizeToAspectRatio(enhanced, 4, 5);
      const instagramPortraitUrl = await this.uploadToS3(
        instagramPortrait,
        userId,
        artPieceId,
        "instagram_portrait",
        "jpeg"
      );
      variants.push({ type: "instagram_portrait", url: instagramPortraitUrl, buffer: instagramPortrait });

      // Instagram Landscape (1.91:1 ratio)
      const instagramLandscape = await this.resizeToAspectRatio(enhanced, 1.91, 1);
      const instagramLandscapeUrl = await this.uploadToS3(
        instagramLandscape,
        userId,
        artPieceId,
        "instagram_landscape",
        "jpeg"
      );
      variants.push({ type: "instagram_landscape", url: instagramLandscapeUrl, buffer: instagramLandscape });

      // X Square (1:1 ratio)
      const xSquare = await this.resizeToAspectRatio(enhanced, 1, 1);
      const xSquareUrl = await this.uploadToS3(xSquare, userId, artPieceId, "x_square", "jpeg");
      variants.push({ type: "x_square", url: xSquareUrl, buffer: xSquare });

      // X Wide (16:9 ratio)
      const xWide = await this.resizeToAspectRatio(enhanced, 16, 9);
      const xWideUrl = await this.uploadToS3(xWide, userId, artPieceId, "x_wide", "jpeg");
      variants.push({ type: "x_wide", url: xWideUrl, buffer: xWide });

      // Inverted (for artistic effect)
      const inverted = await sharp(enhanced)
        .negate()
        .toBuffer();
      const invertedUrl = await this.uploadToS3(inverted, userId, artPieceId, "inverted", "jpeg");
      variants.push({ type: "inverted", url: invertedUrl, buffer: inverted });

      // Cropped (center crop, square)
      const cropped = await this.centerCrop(enhanced, 1, 1);
      const croppedUrl = await this.uploadToS3(cropped, userId, artPieceId, "cropped", "jpeg");
      variants.push({ type: "cropped", url: croppedUrl, buffer: cropped });

      return variants;
    } catch (error) {
      console.error("[ImageProcessingService] Variant generation failed:", error);
      throw error;
    }
  }

  /**
   * Resize image to specific aspect ratio
   */
  private async resizeToAspectRatio(
    imageBuffer: Buffer,
    ratioWidth: number,
    ratioHeight: number
  ): Promise<Buffer> {
    try {
      const metadata = await sharp(imageBuffer).metadata();
      if (!metadata.width || !metadata.height) {
        throw new Error("Cannot determine image dimensions");
      }

      const targetAspectRatio = ratioWidth / ratioHeight;
      const currentAspectRatio = metadata.width / metadata.height;

      let width = metadata.width;
      let height = metadata.height;

      if (currentAspectRatio > targetAspectRatio) {
        // Image is wider than target, crop width
        width = Math.round(metadata.height * targetAspectRatio);
      } else {
        // Image is taller than target, crop height
        height = Math.round(metadata.width / targetAspectRatio);
      }

      const left = Math.round((metadata.width - width) / 2);
      const top = Math.round((metadata.height - height) / 2);

      return await sharp(imageBuffer)
        .extract({ left, top, width, height })
        .resize(1080, Math.round(1080 / targetAspectRatio), {
          fit: "fill",
        })
        .jpeg({ quality: 85, progressive: true })
        .toBuffer();
    } catch (error) {
      console.error("[ImageProcessingService] Aspect ratio resize failed:", error);
      throw error;
    }
  }

  /**
   * Center crop image to specific aspect ratio
   */
  private async centerCrop(
    imageBuffer: Buffer,
    ratioWidth: number,
    ratioHeight: number
  ): Promise<Buffer> {
    return this.resizeToAspectRatio(imageBuffer, ratioWidth, ratioHeight);
  }

  /**
   * Upload processed image to S3
   */
  private async uploadToS3(
    imageBuffer: Buffer,
    userId: number,
    artPieceId: number,
    variantType: string,
    format: string
  ): Promise<string> {
    try {
      const timestamp = Date.now();
      const key = `art-curator/${userId}/pieces/${artPieceId}/${variantType}-${timestamp}.${format}`;
      const mimeType = format === "webp" ? "image/webp" : `image/${format}`;

      const { url } = await storagePut(key, imageBuffer, mimeType);
      return url;
    } catch (error) {
      console.error("[ImageProcessingService] S3 upload failed:", error);
      throw error;
    }
  }

  /**
   * Get image metadata
   */
  async getImageMetadata(imageBuffer: Buffer) {
    try {
      return await sharp(imageBuffer).metadata();
    } catch (error) {
      console.error("[ImageProcessingService] Metadata extraction failed:", error);
      throw error;
    }
  }
}

/**
 * Factory function to create image processing service
 */
export function createImageProcessingService(): ImageProcessingService {
  return new ImageProcessingService();
}

export type { ImageVariant };
