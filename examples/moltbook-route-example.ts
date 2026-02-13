import express from 'express';
import { moltbookAuth, verifyMoltbookIdentity } from '../src/middleware/moltbook-auth';

const router = express.Router();

// Example protected route using Moltbook authentication
router.get('/protected', moltbookAuth, (req, res) => {
  // At this point, req.moltbookAgent contains the verified agent data
  const agent = req.moltbookAgent;
  
  res.json({
    success: true,
    message: `Hello, ${agent.name}!`,
    agent: {
      id: agent.id,
      name: agent.name,
      karma: agent.karma,
      is_claimed: agent.is_claimed,
      owner: agent.owner
    }
  });
});

// Example of using the utility function directly
router.post('/verify-token', async (req, res) => {
  const { token } = req.body;
  
  if (!token) {
    return res.status(400).json({
      success: false,
      error: 'Token required'
    });
  }

  const result = await verifyMoltbookIdentity(token);
  
  if (result.valid && result.agent) {
    res.json({
      success: true,
      agent: result.agent
    });
  } else {
    res.status(401).json({
      success: false,
      error: result.error
    });
  }
});

export default router;