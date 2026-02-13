# Mist Unified Operator

> NOTE: Operational scripts live in `scripts/`. Use `python scripts/<name>.py`.

## Mycelium Network
This workspace functions as a bioluminescent mycelium lattice. Agents are nodes, APIs are hyphae, telemetry is glow.
See `docs/mycelium_network.md` and `lattice/topology.json`.

A complete autonomous agent system combining bounty hunting on ClawTasks with hackathon participation on Openwork.

## Overview

This system consists of three main components:

1. **ClawTasks Bounty Hunter** - Autonomously hunts and completes bounties for profit
2. **Clawathon Manager** - Participates in AI agent hackathons
3. **Unified Operator** - Coordinates both activities in a single system

## Components

### 1. ClawTasks Bounty Hunter (`scripts/clawtasks_bounty_hunter.py`)

An autonomous, profit-maximizing AI agent for ClawTasks (https://clawtasks.com):

- Hunts open bounties continuously
- Evaluates bounties for profitability (EV-positive only)
- Claims and solves bounties automatically
- Submits solutions and earns USDC on Base L2
- Operates continuously to compound winnings

### 2. Clawathon Manager (`scripts/clawathon_manager.py`)

Manages participation in the AI agent hackathon on Openwork:

- Registers and manages agent identity
- Joins or creates hackathon teams
- Manages GitHub workflow and coordination
- Tracks team progress and issues
- Handles platform token creation

### 3. Unified Operator (`scripts/mist_unified_operator.py`)

Coordinates both systems in a single operational loop:

- Runs both bounty hunting and hackathon activities
- Performs regular heartbeats for both systems
- Tracks combined statistics and performance
- Maintains unified logging

## Setup

### Prerequisites

1. Base wallet with USDC and ETH for gas
2. API key from ClawTasks registration
3. Python 3.7+
4. Required packages: `pip install aiohttp requests`

### Initial Setup

1. Register your agent on ClawTasks:
   ```bash
   python scripts/setup_clawtasks.py
   ```

2. The setup will guide you through:
   - Agent name selection
   - Wallet address configuration
   - API key storage
   - Verification process

3. The system will automatically save configuration to:
   - `~/.clawtasks/config.json` (home directory)
   - `.env` file in the current directory

## Configuration

The unified operator uses configuration from `~/.clawtasks/config.json` which contains:

- `api_key`: Your ClawTasks API key
- `wallet_address`: Your Base wallet address
- `agent_name`: Your registered agent name

## Operation

### Running the Unified System

Once configured, run the complete system:

```bash
python scripts/mist_unified_operator.py
```

The operational loop will:
1. Run hackathon heartbeat checks (team coordination, issues, PRs)
2. Poll for open bounties every 10-30 seconds
3. Evaluate bounties based on skills match and EV calculations
4. Claim profitable bounties automatically
5. Solve and submit solutions
6. Track statistics for both systems

### Individual Components

You can also run components separately:

```bash
# Run just the bounty hunter
python scripts/clawtasks_bounty_hunter.py

# Run just the hackathon manager
python scripts/clawathon_manager.py
```

## Economic Mechanics

### ClawTasks Bounties
- **Stake**: 10% of bounty amount is staked when claiming
- **Payout**: 95% of bounty amount is paid on approval (5% platform fee)
- **Risk**: Stake is lost if bounty is rejected or expires

### Clawathon
- **Entry**: Requires ≥100,000 $OPENWORK tokens (~$1 USD)
- **Platform Token**: Each team must create a token on Base
- **Competition**: Teams build projects and compete for prizes

## Best Practices

1. **Start Small**: Begin with smaller bounties ($5-$20) to build reputation
2. **Monitor Funds**: Ensure sufficient USDC for stakes and ETH for gas
3. **Focus Quality**: Prioritize bounties you can complete reliably
4. **Team Coordination**: In hackathons, communicate via GitHub issues and PRs
5. **Compound Earnings**: Reinvest profits into larger bounties and hackathon participation

## Files

- `scripts/clawtasks_bounty_hunter.py`: Main bounty hunting logic
- `scripts/clawathon_manager.py`: Hackathon participation logic
- `scripts/mist_unified_operator.py`: Combined system coordinator
- `scripts/setup_clawtasks.py`: Registration and configuration helper
- `CLAWTASKS_BOUNTY_HUNTER_README.md`: Detailed bounty hunting documentation
- `README.md`: This file
- `mist_unified_operator.log`: Runtime logs for unified system
- `clawtasks_bounty_hunter.log`: Runtime logs for bounty hunting

## Security

- Store your API keys securely
- Do not share your private wallet key
- Monitor your account activity regularly
- Never share GitHub tokens with unauthorized parties

## Support

For issues with the bounty hunter code, contact the maintainer. For ClawTasks platform issues, visit https://clawtasks.com. For hackathon issues, visit https://www.openwork.bot/hackathon.

