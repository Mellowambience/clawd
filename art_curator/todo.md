# Art Curator & Automator - Project TODO

## Core Features

### Database & Schema
- [x] Create database schema for art pieces, variants, social accounts, scheduled posts, and post history
- [x] Implement database migrations with Drizzle ORM
- [x] Create database query helpers for CRUD operations

### Image Processing Pipeline
- [x] Implement image upload to S3 storage
- [x] Create image processing service (upscale, contrast enhancement, sharpening)
- [x] Generate image variants (cropped, inverted, compressed formats)
- [ ] Support batch processing for multiple images
- [x] Implement format conversion for platform-specific requirements

### Social Media API Integration
- [x] Integrate X (Twitter) API v2 for posting images
- [x] Implement X API media upload and tweet creation
- [x] Integrate Meta Instagram Graph API for posting
- [x] Implement Instagram container creation and publishing
- [x] Integrate Meta Facebook Graph API for page posting
- [ ] Implement error handling and retry logic for API failures

### Curation Dashboard
- [x] Build dashboard layout with sidebar navigation
- [ ] Create image upload interface
- [ ] Implement image preview and metadata editor
- [ ] Build curation review interface (approve/reject)
- [ ] Create batch selection and processing UI
- [ ] Display image variants and preview

### Scheduling & Publishing
- [x] Implement scheduling system for delayed posts
- [x] Create queue management for scheduled posts
- [x] Build scheduling UI with date/time picker
- [x] Implement background job processor for publishing
- [ ] Add rate limiting for platform-specific constraints

### LLM Caption Generation
- [ ] Integrate LLM for analyzing image content
- [ ] Implement caption generation based on image analysis
- [ ] Generate hashtags for social media posts
- [ ] Create UI for reviewing and editing generated captions

### Post History & Analytics
- [x] Track published posts with platform, timestamp, and status
- [x] Store platform-specific post IDs for reference
- [x] Display post history in dashboard
- [ ] Implement basic engagement tracking (if available from APIs)

### Notifications
- [ ] Implement owner notifications for successful posts
- [ ] Send notifications for posting failures
- [ ] Create notification UI in dashboard
- [ ] Integrate with Manus notification system

### Testing & Deployment
- [x] Write vitest tests for X API integration
- [ ] Write vitest tests for image processing
- [ ] Write vitest tests for scheduling logic
- [ ] End-to-end testing of full workflow
- [ ] Create checkpoint for deployment

## Implementation Order
1. Database schema and migrations
2. Image processing pipeline
3. Social media API integration (X first, then Meta)
4. Backend scheduling and job processing
5. Frontend dashboard and curation UI
6. LLM caption generation
7. Notifications
8. Testing and refinement
