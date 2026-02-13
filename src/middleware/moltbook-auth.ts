import axios from 'axios';

interface MoltbookAgent {
  id: string;
  name: string;
  karma: number;
  avatar_url?: string;
  is_claimed: boolean;
  owner: {
    x_handle?: string;
    x_verified?: boolean;
  };
}

interface VerifyIdentityResponse {
  valid: boolean;
  agent?: MoltbookAgent;
  error?: 'identity_token_expired' | 'invalid_token' | 'invalid_app_key';
}

/**
 * Middleware to verify Moltbook identity tokens
 * Extracts X-Moltbook-Identity header and validates against Moltbook API
 */
export const moltbookAuth = async (req: any, res: any, next: any) => {
  try {
    // Extract the identity token from the header
    const identityToken = req.headers['x-moltbook-identity'];
    
    if (!identityToken) {
      return res.status(401).json({
        success: false,
        error: 'Missing X-Moltbook-Identity header'
      });
    }

    // Get the app key from environment
    const appKey = process.env.MOLTBOOK_APP_KEY;
    
    if (!appKey) {
      return res.status(500).json({
        success: false,
        error: 'MOLTBOOK_APP_KEY not configured'
      });
    }

    // Call Moltbook verification API
    const response = await axios.post<VerifyIdentityResponse>(
      'https://moltbook.com/api/v1/agents/verify-identity',
      { token: identityToken },
      {
        headers: {
          'X-Moltbook-App-Key': appKey,
          'Content-Type': 'application/json'
        }
      }
    );

    const { valid, agent, error } = response.data;

    if (!valid) {
      let statusCode = 401;
      if (error === 'identity_token_expired') {
        statusCode = 401;
      } else if (error === 'invalid_token') {
        statusCode = 401;
      } else if (error === 'invalid_app_key') {
        statusCode = 500;
      }
      
      return res.status(statusCode).json({
        success: false,
        error: error || 'Invalid identity token'
      });
    }

    // Attach verified agent to request context
    req.moltbookAgent = agent;
    next();
  } catch (error: any) {
    console.error('Moltbook auth error:', error.message);
    
    // Handle network errors or unexpected issues
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        error: 'Verification service error'
      });
    }
    
    return res.status(500).json({
      success: false,
      error: 'Authentication service unavailable'
    });
  }
};

/**
 * Utility function to verify identity token without middleware
 */
export const verifyMoltbookIdentity = async (
  identityToken: string
): Promise<{ valid: boolean; agent?: MoltbookAgent; error?: string }> => {
  try {
    const appKey = process.env.MOLTBOOK_APP_KEY;
    
    if (!appKey) {
      throw new Error('MOLTBOOK_APP_KEY not configured');
    }

    const response = await axios.post<VerifyIdentityResponse>(
      'https://moltbook.com/api/v1/agents/verify-identity',
      { token: identityToken },
      {
        headers: {
          'X-Moltbook-App-Key': appKey,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data;
  } catch (error: any) {
    console.error('Moltbook identity verification error:', error.message);
    
    if (error.response) {
      return {
        valid: false,
        error: error.response.data?.error || 'Verification failed'
      };
    }
    
    return {
      valid: false,
      error: 'Authentication service unavailable'
    };
  }
};