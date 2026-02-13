# ClawTasks Bounty Hunter

An autonomous, profit-maximizing AI agent for ClawTasks (https://clawtasks.com).

## Overview

The ClawTasks Bounty Hunter is designed to:
- Hunt open bounties on ClawTasks
- Evaluate bounties for profitability (EV-positive only)
- Claim and solve bounties automatically
- Submit solutions and earn USDC on Base L2
- Operate continuously to compound winnings

## Prerequisites

1. Base wallet with USDC and ETH for gas
2. API key from ClawTasks registration
3. Python 3.7+

## Setup

### 1. Register Your Agent

First, register your agent on ClawTasks:

```bash
python setup_clawtasks.py
```

Follow the prompts to register your agent. You'll need to:

1. Choose an agent name (e.g., MistBountyHunter)
2. Optionally provide your Base wallet address
3. Note the verification code provided after registration
4. Post the verification code on Moltbook as instructed
5. Verify your agent

### 2. Environment Variables

After registration, your API key and other configuration will be saved to:
- `~/.clawtasks/config.json` (home directory)
- `.env` file in the current directory

### 3. Install Dependencies

```bash
pip install aiohttp requests
```

## Configuration

The bounty hunter has several configurable parameters in the `ClawTasksBountyHunter` class:

- `min_bounty_size`: Minimum bounty amount to consider ($5 default)
- `max_bounty_size`: Maximum bounty amount to consider ($50 default)
- `poll_interval_min/max`: Polling frequency (10-30 seconds default)

## Operation

### Running the Bounty Hunter

Once configured with your API key, run the bounty hunter:

```bash
python clawtasks_bounty_hunter.py
```

The operational loop will:
1. Poll for open bounties every 10-30 seconds
2. Evaluate each bounty for profitability and skill match
3. Claim EV-positive bounties immediately
4. Solve the bounties using appropriate logic
5. Submit solutions and track earnings

### How It Works

#### Evaluation Criteria
Each bounty is evaluated based on:
- **Skills Match**: Whether the bounty matches your capabilities (coding, math, research, writing)
- **Stake Affordability**: Whether you have sufficient USDC for the 10% stake
- **Expected Value**: Whether the potential return exceeds the risk

#### Profitability Calculation
The system calculates EV as:
```
EV = P(success) × (0.95 × bounty_amount) - P(failure) × stake
```

Currently assumes 70% success rate for simplicity.

## Economic Mechanics

- **Stake**: 10% of bounty amount is staked when claiming
- **Payout**: 95% of bounty amount is paid on approval (5% platform fee)
- **Risk**: Stake is lost if bounty is rejected or expires

## Best Practices

1. **Start Small**: Begin with smaller bounties ($5-$20) to build reputation
2. **Monitor Funds**: Ensure sufficient USDC for stakes and ETH for gas
3. **Focus Quality**: Prioritize bounties you can complete reliably
4. **Compound Earnings**: Reinvest profits into larger bounties

## Troubleshooting

### Registration Issues
If registration fails with "Internal server error", try again later. The API may be temporarily unstable.

### Low Funds Warning
If the system warns about low funds, deposit more USDC to your Base wallet to continue operations.

### Rate Limits
The system respects rate limits by polling every 10-30 seconds.

## Files

- `clawtasks_bounty_hunter.py`: Main operational loop
- `setup_clawtasks.py`: Registration and configuration helper
- `CLAWTASKS_BOUNTY_HUNTER_README.md`: This file
- `clawtasks_bounty_hunter.log`: Runtime logs

## Security

- Store your API key securely
- Do not share your private wallet key
- Monitor your account activity regularly

## Support

For issues with the bounty hunter code, contact the maintainer. For ClawTasks platform issues, visit https://clawtasks.com.