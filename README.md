# 🦑 Squid DAO Vote Calculator

> **Signal vote caps at 8 tokens, Squid has too many tentacles**

A Vyper smart contract that aggregates voting power across Curve, Convex, and Stake DAO for the [Squid DAO](https://snapshot.box/#/s:leviathannews.eth) governance system. Unlike Snapshot's 8-token limit, this contract supports **9 tentacles** worth of token sources, providing comprehensive voting power calculation.

## 🚀 Deployment

**Contract Address**: [`0xa3059E86548a4720AD28c881B701c6f02120164a`](https://fraxscan.com/address/0xa3059E86548a4720AD28c881B701c6f02120164a)  
**Network**: Fraxtal Mainnet  
**Explorer**: [Fraxtal Scan](https://fraxscan.com/address/0xa3059E86548a4720AD28c881B701c6f02120164a)

## 🦑 The Nine-Tentacled Squid

This contract aggregates voting power from **9 different token sources**:

### 🦑🛀 Tentacle 1: Naked SQUID
- **Raw, uncensored SQUID token holdings**
- **Address**: [`0x6e58089d8E8f664823d26454f49A5A0f2fF697Fe`](https://fraxscan.com/address/0x6e58089d8E8f664823d26454f49A5A0f2fF697Fe)

### 🦑💎 Tentacle 2: SQUID/ETH LP (Curve)
- **Curve pool liquidity provider tokens**
- **Address**: [`0x277FA53c8a53C880E0625c92C92a62a9F60f3f04`](https://fraxscan.com/address/0x277FA53c8a53C880E0625c92C92a62a9F60f3f04)

### 🦑💎 Tentacle 3: SQUID/ETH LP (Gauge)
- **Curve gauge staked LP tokens**
- **Address**: [`0xe5E5ed1B50AE33E66ca69dF17Aa6381FDe4e9C7e`](https://fraxscan.com/address/0xe5E5ed1B50AE33E66ca69dF17Aa6381FDe4e9C7e)

### 🦑💎 Tentacle 4: SQUID/ETH LP (Convex)
- **Convex boosted LP positions**
- **Address**: [`0x29FF8F9ACb27727D8A2A52D16091c12ea56E9E4d`](https://fraxscan.com/address/0x29FF8F9ACb27727D8A2A52D16091c12ea56E9E4d)

### 🦑💎 Tentacle 5: SQUID/ETH LP (Stake DAO)
- **Stake DAO boosted LP positions**
- **Address**: [`0x8CDCDccAB3fC79c267B8361AdDAefD3aADaB9778`](https://fraxscan.com/address/0x8CDCDccAB3fC79c267B8361AdDAefD3aADaB9778)

### 🦑🪶 Tentacle 6: SQUID/SQUILL LP (Curve)
- **Curve pool liquidity provider tokens**
- **Address**: [`0xb2B1458960E4d64716c8C472c114441A02fBA1De`](https://fraxscan.com/address/0xb2B1458960E4d64716c8C472c114441A02fBA1De)

### 🦑🪶 Tentacle 7: SQUID/SQUILL LP (Gauge)
- **Curve gauge staked LP tokens**
- **Address**: [`0x9bC291018e0434a21218A16005B0e198b4814ba8`](https://fraxscan.com/address/0x9bC291018e0434a21218A16005B0e198b4814ba8)

### 🦑🪶 Tentacle 8: SQUID/SQUILL LP (Convex)
- **Convex boosted LP positions**
- **Address**: [`0x1CC03c1C714f767ca866A3Fa58c9153b1C087E85`](https://fraxscan.com/address/0x1CC03c1C714f767ca866A3Fa58c9153b1C087E85)

### 🦑🪶 Tentacle 9: SQUID/SQUILL LP (Stake DAO)
- **Stake DAO boosted LP positions**
- **Address**: [`0x9C1a1b52Bf2c42B6e7E2dCdAEF260b60386Ad76b`](https://fraxscan.com/address/0x9C1a1b52Bf2c42B6e7E2dCdAEF260b60386Ad76b)

## 🏗️ Multi-Protocol Architecture

### DeFi Protocol Integration
```
SquidDaoVote.vy
├── 🦑🛀 Naked SQUID Tokens
├── 🦑💎 SQUID/ETH LP Positions
│   ├── Curve Pool (0x277FA53c8a53C880E0625c92C92a62a9F60f3f04)
│   └── Curve Gauge (0xe5E5ed1B50AE33E66ca69dF17Aa6381FDe4e9C7e)
│   ├── Convex (0x29FF8F9ACb27727D8A2A52D16091c12ea56E9E4d)
│   ├── Stake DAO (0x8CDCDccAB3fC79c267B8361AdDAefD3aADaB9778)
└── 🦑🪶 SQUID/SQUILL LP Positions
    ├── Curve Pool (0xb2B1458960E4d64716c8C472c114441A02fBA1De)
    ├── Convex (0x1CC03c1C714f767ca866A3Fa58c9153b1C087E85)
    └── Stake DAO (0x9C1a1b52Bf2c42B6e7E2dCdAEF260b60386Ad76b)
```

### Price Oracle Integration
- **ETH/USD**: ThreeCrypto oracle ([`0xa0D3911349e701A1F49C1Ba2dDA34b4ce9636569`](https://fraxscan.com/address/0xa0D3911349e701A1F49C1Ba2dDA34b4ce9636569))
- **SQUID/ETH**: TwoCrypto oracle ([`0x277FA53c8a53C880E0625c92C92a62a9F60f3f04`](https://fraxscan.com/address/0x277FA53c8a53C880E0625c92C92a62a9F60f3f04))
- **SQUILL/SQUID**: TwoCrypto oracle ([`0xb2B1458960E4d64716c8C472c114441A02fBA1De`](https://fraxscan.com/address/0xb2B1458960E4d64716c8C472c114441A02fBA1De))

## 🔒 Security Features

### Dust Protection System
The contract implements sophisticated dust protection to prevent inflation attacks:

```vyper
if bal < 10_000_000:  # 10M wei threshold
    return 0
```

- **Threshold**: 10 million wei (0.00000001 LP = ~$0.0000003 USD)
- **Protection**: Eliminates dust-based voting power inflation
- **Impact**: Only poors affected
- **Coverage**: Both SQUID/ETH and SQUILL LP calculations

### Multi-Layer Validation
- **Division by zero protection**
- **Price oracle validation**
- **Curve pool integration safety**
- **Precision loss prevention**

## 📁 Project Structure

```
squid-dao/
├── contracts/
│   ├── SquidDaoVote.vy          # Main contract (393 lines)
│   └── test/
│       └── ERC20.vy             # Test token contract
├── deployments/
│   └── squid_dao_vote_fraxtal.json  # Deployment artifact
├── tests/
│   ├── conftest.py              # Test configuration
│   ├── test_balance.py          # Core balance tests
│   ├── test_census_generic.py   # Generic census tests (AI generated)
│   └── test_lp_equivalent_edge_cases.py  # Edge case tests (AI generated)
├── scripts/
│   └── deploy.py               # Deployment script
├── requirements.in             # Python dependencies
```

## 🧪 Comprehensive Testing

### Test Suite Coverage
- **100% test coverage** covering all functionality
- **Fork testing** against Fraxtal mainnet
- **Edge case coverage** including dust protection
- **Multi-protocol testing** across Curve, Convex, and Stake DAO
- **Generic tests** safe for public repository

### Running Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest --fork -v

# Run specific test file
pytest tests/test_balance.py --fork -v
```

### Test Categories
- **Balance calculations**: Core voting power logic
- **LP equivalency**: Curve pool integration
- **Price oracles**: External price feeds
- **Edge cases**: Dust protection and precision
- **Census functionality**: Voter aggregation
- **Multi-protocol**: Curve, Convex, Stake DAO integration

## 🔧 Development

### Prerequisites
- Python 3.11+
- Vyper compiler
- Titanoboa testing framework
- Fraxtal RPC access

### Setup
```bash
# Clone repository
git clone <repository-url>
cd squid-dao

# Create virtual environment
python -m venv dao-env
source dao-env/bin/activate  # Linux/Mac
# or
dao-env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Contract Compilation
```bash
# Compile contract
vyper contracts/SquidDaoVote.vy
```

## 📈 Governance Integration

The contract is designed for integration with governance systems:

- **Standardized interface**: `balanceOf(address)` returns voting power
- **SQUID-equivalent**: All balances normalized to SQUID units
- **Real-time calculation**: Live price feeds and pool data
- **Dust protection**: Prevents manipulation attacks
- **Multi-protocol support**: Curve, Convex, Stake DAO integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License
