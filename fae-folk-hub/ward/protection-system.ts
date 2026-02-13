/**
 * Fae Folk Community Hub - Ward Protection System
 * Security and privacy protection
 */

interface FaeUserCredentials {
  userId: string;
  publicKey: string;
  privateKey?: string;
  faeName: string;
  joinDate: Date;
  reputation: number;
  verified: boolean;
}

interface AccessControlRule {
  id: string;
  resource: string; // 'grove', 'sacred_circle', 'mars_dream', etc.
  subject: string; // userId or role
  action: 'read' | 'write' | 'moderate' | 'admin' | '*';
  condition?: string; // Optional condition
  effect: 'allow' | 'deny';
  priority: number; // Lower numbers have higher priority
}

interface PrivacySetting {
  userId: string;
  visibility: 'public' | 'friends' | 'circle' | 'private';
  contentFilter: string[]; // Categories to filter
  dataSharing: 'none' | 'minimal' | 'standard' | 'generous';
  activityVisibility: 'visible' | 'limited' | 'hidden';
}

interface SecurityIncident {
  id: string;
  timestamp: Date;
  type: 'unauthorized_access' | 'privacy_violation' | 'harassment' | 'misconduct' | 'breach_attempt';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string; // IP, userId, or other identifier
  target: string; // Affected resource or user
  description: string;
  resolved: boolean;
  resolutionNotes?: string;
}

interface ConsentRecord {
  id: string;
  fromUserId: string;
  toUserId: string;
  scope: 'message' | 'presence' | 'data' | 'connection' | 'activity';
  granted: boolean;
  timestamp: Date;
  expiration?: Date;
}

class WardProtectionSystem {
  private userCredentials: Map<string, FaeUserCredentials> = new Map();
  private accessControlRules: AccessControlRule[] = [];
  private privacySettings: Map<string, PrivacySetting> = new Map();
  private securityIncidents: SecurityIncident[] = [];
  private consentRecords: Map<string, ConsentRecord> = new Map();
  private activeWards: Map<string, boolean> = new Map(); // userId -> ward active
  private trustedNodes: Set<string> = new Set(); // Set of verified node IDs

  constructor() {
    this.initializeDefaultRules();
  }

  /**
   * Initialize default access control rules
   */
  private initializeDefaultRules(): void {
    // Everyone can read public grove information
    this.addRule({
      resource: 'grove',
      subject: '*',
      action: 'read',
      effect: 'allow',
      priority: 100
    });

    // Users can read their own information
    this.addRule({
      resource: 'user:*',
      subject: 'own',
      action: 'read',
      effect: 'allow',
      priority: 50
    });

    // Users can write their own information
    this.addRule({
      resource: 'user:*',
      subject: 'own',
      action: 'write',
      effect: 'allow',
      priority: 50
    });

    // Deny all access by default (explicit allow policy)
    this.addRule({
      resource: '*',
      subject: '*',
      action: '*' as any, // Using 'any' to bypass type checking for wildcard
      effect: 'deny',
      priority: 10
    });
  }

  /**
   * Add a user credential
   */
  addUserCredential(credentials: Omit<FaeUserCredentials, 'reputation' | 'verified' | 'userId' | 'joinDate'>): string {
    const userId = this.generateId();
    const newCredentials: FaeUserCredentials = {
      ...credentials,
      userId,
      reputation: 0.5, // New users start with neutral reputation
      verified: false, // Needs verification
      joinDate: new Date()
    };

    this.userCredentials.set(userId, newCredentials);
    
    // Set default privacy settings
    this.setPrivacySettings(userId, {
      userId,
      visibility: 'friends',
      contentFilter: [],
      dataSharing: 'minimal',
      activityVisibility: 'limited'
    });

    // Create a personal ward for the user
    this.activeWards.set(userId, true);

    return userId;
  }

  /**
   * Verify a user's identity
   */
  verifyUser(userId: string): boolean {
    const credentials = this.userCredentials.get(userId);
    if (!credentials) return false;

    // In a real implementation, this would involve cryptographic verification
    credentials.verified = true;
    credentials.reputation = Math.min(1, credentials.reputation + 0.2); // Boost reputation for verification

    // Add trusted user rules
    this.addRule({
      resource: 'sacred_circle',
      subject: userId,
      action: 'read',
      effect: 'allow',
      priority: 75
    });

    return true;
  }

  /**
   * Add an access control rule
   */
  addRule(rule: Omit<AccessControlRule, 'id'>): string {
    const ruleId = this.generateId();
    const newRule: AccessControlRule = {
      ...rule,
      id: ruleId
    };

    this.accessControlRules.push(newRule);
    // Sort by priority (lower number = higher priority)
    this.accessControlRules.sort((a, b) => a.priority - b.priority);

    return ruleId;
  }

  /**
   * Check if a user has permission to perform an action
   */
  checkPermission(userId: string, resource: string, action: string): boolean {
    // Find all applicable rules
    const applicableRules = this.accessControlRules.filter(rule => {
      return (rule.resource === resource || rule.resource === '*') &&
             (rule.subject === userId || rule.subject === '*' || rule.subject === 'own' || 
              (rule.subject === 'own' && resource.startsWith(`user:${userId}`))) &&
             (rule.action === action || rule.action === '*');
    });

    // Apply rules in priority order
    for (const rule of applicableRules) {
      if (rule.effect === 'allow') {
        return true;
      } else if (rule.effect === 'deny') {
        return false;
      }
    }

    // Default deny if no rules match
    return false;
  }

  /**
   * Set privacy settings for a user
   */
  setPrivacySettings(userId: string, settings: Partial<PrivacySetting>): void {
    const currentSettings = this.privacySettings.get(userId) || {
      userId,
      visibility: 'public',
      contentFilter: [],
      dataSharing: 'minimal',
      activityVisibility: 'visible'
    };

    const newSettings: PrivacySetting = {
      ...currentSettings,
      ...settings
    };

    this.privacySettings.set(userId, newSettings);
  }

  /**
   * Get privacy settings for a user
   */
  getPrivacySettings(userId: string): PrivacySetting | undefined {
    return this.privacySettings.get(userId);
  }

  /**
   * Record a consent between users
   */
  recordConsent(fromUserId: string, toUserId: string, scope: ConsentRecord['scope'], granted: boolean, expiration?: Date): string {
    const consentId = this.generateId();
    const consent: ConsentRecord = {
      id: consentId,
      fromUserId,
      toUserId,
      scope,
      granted,
      timestamp: new Date(),
      expiration
    };

    this.consentRecords.set(consentId, consent);

    // Adjust reputation based on consent granting
    if (granted) {
      const toUser = this.userCredentials.get(toUserId);
      if (toUser) {
        toUser.reputation = Math.min(1, toUser.reputation + 0.05);
      }
    }

    return consentId;
  }

  /**
   * Check if consent exists between users for a specific scope
   */
  checkConsent(fromUserId: string, toUserId: string, scope: ConsentRecord['scope']): boolean {
    const consent = Array.from(this.consentRecords.values()).find(c =>
      c.fromUserId === fromUserId &&
      c.toUserId === toUserId &&
      c.scope === scope &&
      c.granted &&
      (!c.expiration || c.expiration > new Date())
    );

    return !!consent;
  }

  /**
   * Create a security incident report
   */
  reportSecurityIncident(type: SecurityIncident['type'], severity: SecurityIncident['severity'], source: string, target: string, description: string): string {
    const incidentId = this.generateId();
    const incident: SecurityIncident = {
      id: incidentId,
      timestamp: new Date(),
      type,
      severity,
      source,
      target,
      description,
      resolved: false
    };

    this.securityIncidents.push(incident);

    // Adjust reputation of source if applicable
    if (source.startsWith('user:')) {
      const userId = source.substring(5);
      const user = this.userCredentials.get(userId);
      if (user && severity !== 'low') {
        user.reputation = Math.max(0, user.reputation - (severity === 'critical' ? 0.3 : 0.1));
      }
    }

    return incidentId;
  }

  /**
   * Resolve a security incident
   */
  resolveSecurityIncident(incidentId: string, resolutionNotes: string): boolean {
    const incident = this.securityIncidents.find(i => i.id === incidentId);
    if (!incident) return false;

    incident.resolved = true;
    incident.resolutionNotes = resolutionNotes;

    // If the incident was resolved favorably, potentially restore some reputation
    if (incident.source.startsWith('user:')) {
      const userId = incident.source.substring(5);
      const user = this.userCredentials.get(userId);
      if (user && incident.severity !== 'critical') {
        user.reputation = Math.min(1, user.reputation + 0.05);
      }
    }

    return true;
  }

  /**
   * Activate a protective ward for a user
   */
  activateWard(userId: string): boolean {
    const user = this.userCredentials.get(userId);
    if (!user) return false;

    this.activeWards.set(userId, true);
    return true;
  }

  /**
   * Deactivate a protective ward for a user
   */
  deactivateWard(userId: string): boolean {
    const user = this.userCredentials.get(userId);
    if (!user) return false;

    this.activeWards.set(userId, false);
    return true;
  }

  /**
   * Check if a ward is active for a user
   */
  isWardActive(userId: string): boolean {
    return this.activeWards.get(userId) ?? false;
  }

  /**
   * Add a trusted node to the network
   */
  addTrustedNode(nodeId: string): void {
    this.trustedNodes.add(nodeId);
  }

  /**
   * Check if a node is trusted
   */
  isNodeTrusted(nodeId: string): boolean {
    return this.trustedNodes.has(nodeId);
  }

  /**
   * Filter content based on user's privacy settings
   */
  filterContentForUser(content: any, userId: string, requestingUser: string): any {
    const userSettings = this.privacySettings.get(userId);
    if (!userSettings) return content;

    // Check visibility settings
    if (userSettings.visibility === 'private' && requestingUser !== userId) {
      return null; // Hide content entirely
    }

    if (userSettings.visibility === 'friends' && !this.checkConsent(userId, requestingUser, 'data')) {
      return null; // Hide content from non-friends
    }

    // Apply content filtering
    if (userSettings.contentFilter.length > 0 && content.tags) {
      const hasFilteredTag = content.tags.some((tag: string) => userSettings.contentFilter.includes(tag));
      if (hasFilteredTag) {
        return null; // Filter out content with unwanted tags
      }
    }

    return content;
  }

  /**
   * Get user's reputation
   */
  getUserReputation(userId: string): number | undefined {
    const user = this.userCredentials.get(userId);
    return user ? user.reputation : undefined;
  }

  /**
   * Update user's reputation
   */
  updateUserReputation(userId: string, delta: number): boolean {
    const user = this.userCredentials.get(userId);
    if (!user) return false;

    user.reputation = Math.max(0, Math.min(1, user.reputation + delta));
    return true;
  }

  /**
   * Check if a user is verified
   */
  isUserVerified(userId: string): boolean {
    const user = this.userCredentials.get(userId);
    return user ? user.verified : false;
  }

  /**
   * Get all security incidents
   */
  getSecurityIncidents(): SecurityIncident[] {
    return [...this.securityIncidents];
  }

  /**
   * Get active wards
   */
  getActiveWards(): string[] {
    return Array.from(this.activeWards.entries())
      .filter(([_, active]) => active)
      .map(([userId, _]) => userId);
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Perform security audit
   */
  performSecurityAudit(): {
    totalUsers: number;
    verifiedUsers: number;
    activeWards: number;
    securityIncidents: number;
    averageReputation: number;
    trustedNodes: number;
  } {
    const totalUsers = this.userCredentials.size;
    const verifiedUsers = Array.from(this.userCredentials.values()).filter(u => u.verified).length;
    const activeWards = this.getActiveWards().length;
    const securityIncidents = this.securityIncidents.length;
    const trustedNodes = this.trustedNodes.size;

    const totalReputation = Array.from(this.userCredentials.values()).reduce((sum, user) => sum + user.reputation, 0);
    const averageReputation = totalUsers > 0 ? totalReputation / totalUsers : 0;

    return {
      totalUsers,
      verifiedUsers,
      activeWards,
      securityIncidents,
      averageReputation,
      trustedNodes
    };
  }
}

export { WardProtectionSystem, FaeUserCredentials, AccessControlRule, PrivacySetting, SecurityIncident, ConsentRecord };