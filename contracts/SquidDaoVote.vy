# version 0.4.3

"""
@title SQUID DAO Vote Calculator
@notice Signal vote caps at 8 tokens, Squid has too many tentacles
@dev Combines naked SQUID plus equivalent LPs (SQUID/ETH) via Curve, Convex, Stake DAO
@author Leviathan News
@license MIT

                         ██████████████
                      ████████████████████
                    █████████████████████████
                  ████████████████████████████
                 ██████████████████████████████
                ████████████████████████████████
               ██████████████████████████████████
               ██████████████████████████████████
               ██████████████████████████████████
               █████     ██████████████     █████
               ████       ████████████       ████
                ███       ████████████       ███
                ████     ██████████████     ████
                  ████████████████████████████
                   ██████████████████████████
   ██████████       ████████████████████████       ██████████
 ██████████████     ████████████████████████     ██████████████
████████████████   ██████████████████████████   ████████████████
███████ ████████  ████████████████████████████  ████████ ███████
██████ █████████ ██████████████████████████████ █████████ ██████
███████ ██████ ██████████ ████████████ ██████████ ██████ ███████
████████████████████████  ████████████  ████████████████████████
  ████████████████████    ████████████    ████████████████████
   █████████████████     ██████████████     █████████████████
      ███████████████    ██████████████    ███████████████
            ███████████  ██████  ██████  ███████████
           ██████ █████████████  █████████████ ██████
          ██████ ██████████████   █████████████ ██████
          ███████ ████████████    ████████████ ███████
          ███████████████████      ███████████████████
           ██████████████████      ██████████████████
            ███████████████          ███████████████
               ██████████              ██████████

"""

# ============================================================================================
# 🧩 INTERFACES
# ============================================================================================

from ethereum.ercs import IERC20


interface TwoCrypto:
    def price_oracle() -> uint256: view
    def calc_withdraw_one_coin(token_amount: uint256, i: uint256) -> uint256: view
    def coins(i: uint256) -> address: view


interface ThreeCrypto:
    def price_oracle(i: uint256) -> uint256: view


# ============================================================================================
# 💾 STORAGE
# ============================================================================================

# NAKED SQUID 🦑🛀
squid_token: IERC20

# SQUID / ETH LP 🦑💎
squid_eth_lp_token: IERC20
squid_eth_gauge: IERC20
squid_eth_cvx: IERC20
squid_eth_stakedao: IERC20

# SQUID / SQUILL LP 🦑🪶
squill_lp_token: IERC20
squill_gauge: IERC20
squill_cvx: IERC20
squill_stakedao: IERC20

# PRICE ORACLES ⚖️
squid_eth_pool: TwoCrypto
squill_squid_pool: TwoCrypto
eth_usd_pool: ThreeCrypto


# ============================================================================================
# 🚧 CONSTRUCTOR
# ============================================================================================

@deploy
def __init__():

    # NAKED SQUID 🦑🛀
    self.squid_token = IERC20(0x6e58089d8E8f664823d26454f49A5A0f2fF697Fe)

    # SQUID/ETH LP 🦑💎
    self.squid_eth_lp_token = IERC20(0x277FA53c8a53C880E0625c92C92a62a9F60f3f04)
    self.squid_eth_gauge = IERC20(0xe5E5ed1B50AE33E66ca69dF17Aa6381FDe4e9C7e)
    self.squid_eth_cvx = IERC20(0x29FF8F9ACb27727D8A2A52D16091c12ea56E9E4d)
    self.squid_eth_stakedao = IERC20(0x8CDCDccAB3fC79c267B8361AdDAefD3aADaB9778)

    # SQUID/SQUILL LP 🦑🪶
    self.squill_lp_token = IERC20(0xb2B1458960E4d64716c8C472c114441A02fBA1De)
    self.squill_gauge = IERC20(0x9bC291018e0434a21218A16005B0e198b4814ba8)
    self.squill_cvx = IERC20(0x1CC03c1C714f767ca866A3Fa58c9153b1C087E85)
    self.squill_stakedao = IERC20(0x9C1a1b52Bf2c42B6e7E2dCdAEF260b60386Ad76b)

    # PRICE ORACLES ⚖️
    self.squid_eth_pool = TwoCrypto(0x277FA53c8a53C880E0625c92C92a62a9F60f3f04)
    self.squill_squid_pool = TwoCrypto(0xb2B1458960E4d64716c8C472c114441A02fBA1De)
    self.eth_usd_pool = ThreeCrypto(0xa0D3911349e701A1F49C1Ba2dDA34b4ce9636569)


# ============================================================================================
# 👀 VIEW FUNCTIONS
# ============================================================================================

@external
@view
def balanceOf(addr: address) -> uint256:
    """
    @notice Calculate the total SQUID voting power for an address
    @dev Combines three types of token holdings to determine total voting power:
         - Naked SQUID tokens (direct holdings)
         - SQUID/ETH LP tokens (converted to SQUID equivalent)
         - SQUID/SQUILL LP tokens (converted to SQUID equivalent)
    @param addr The address for which to check voting power
    @return Total SQUID equivalent voting power for the address
    """
    total_bal: uint256 = self._squid_balance(addr)
    total_bal += self._squid_lp_balance_in_squid(addr)
    total_bal += self._squill_lp_balance_in_squid(addr)

    return total_bal


# ======================
# NAKED SQUID 🦑🛀
# ======================

@external
@view
def squid_balance(addr: address) -> uint256:
    """
    @notice Get the naked SQUID token balance for an address
    @dev Returns only the direct SQUID token holdings, excluding LP tokens
    @param addr The address for which to check SQUID balance
    @return Amount of naked SQUID tokens held by the address
    """
    return self._squid_balance(addr)


# ======================
# SQUID/ETH LP 🦑💎
# ======================

@external
@view
def squid_lp_balance(addr: address) -> uint256:
    """
    @notice Get the total SQUID/ETH LP token balance for an address
    @dev Includes LP tokens from gauge, Convex, and Stake DAO positions
    @param addr The address for which to check SQUID/ETH LP balance
    @return Total amount of SQUID/ETH LP tokens held by the address
    """
    return self._squid_lp_balance(addr)


@external
@view
def squid_lp_balance_in_squid(addr: address) -> uint256:
    """
    @notice Convert SQUID/ETH LP token balance to SQUID equivalent
    @dev Calculates the SQUID equivalent value of LP tokens using current pool rates
    @param addr The address for which to check SQUID/ETH LP balance
    @return SQUID equivalent value of the address's SQUID/ETH LP tokens
    """
    return self._squid_lp_balance_in_squid(addr)


# ======================
# SQUID/SQUILL LP 🦑🪶
# ======================

@external
@view
def squill_lp_balance(addr: address) -> uint256:
    """
    @notice Get the total SQUID/SQUILL LP token balance for an address
    @dev Includes LP tokens from gauge, Convex, and Stake DAO positions
    @param addr The address to check SQUID/SQUILL LP balance for
    @return Total amount of SQUID/SQUILL LP tokens held by the address
    """
    return self._squill_lp_balance(addr)


@external
@view
def squill_lp_balance_in_squid(addr: address) -> uint256:
    """
    @notice Convert SQUID/SQUILL LP token balance to SQUID equivalent
    @dev Calculates the SQUID equivalent value of SQUILL LP tokens using current pool rates
    @param addr The address to check SQUID/SQUILL LP balance for
    @return SQUID equivalent value of the address's SQUID/SQUILL LP tokens
    """
    return self._squill_lp_balance_in_squid(addr)


# ======================
# PRICE ORACLES ⚖️
# ======================

@external
@view
def eth_price() -> uint256:
    """
    @notice Get the current ETH price in USD
    @dev Fetches ETH/USD price from the Curve ThreeCrypto oracle
    @return Current ETH price in USD (scaled by 10^18)
    """
    return self._eth_usd_price()


@external
@view
def squid_price() -> uint256:
    """
    @notice Get the current SQUID price in USD
    @dev Calculates SQUID/USD price using SQUID/ETH and ETH/USD oracles
    @return Current SQUID price in USD (scaled by 10^18)
    """
    return self._squid_usd_price()


@external
@view
def squill_price() -> uint256:
    """
    @notice Get the current SQUILL price in USD
    @dev Calculates SQUILL/USD price using SQUILL/SQUID and SQUID/USD oracles
    @return Current SQUILL price in USD (scaled by 10^18)
    """
    return self._squill_usd_price()


@external
@view
def squid_lp_equivalent(quantity: uint256 = 10**18) -> uint256:
    """
    @notice Calculate SQUID equivalent for a given amount of SQUID/ETH LP tokens
    @dev Uses the Curve pool's calc_withdraw_one_coin to determine SQUID equivalent
    @param quantity Amount of SQUID/ETH LP tokens to convert (defaults to 1 LP token)
    @return SQUID equivalent amount for the given LP token quantity
    """
    return self._squid_lp_equivalent(quantity)


@external
@view
def squill_lp_equivalent(quantity: uint256 = 10**18) -> uint256:
    """
    @notice Calculate SQUID equivalent for a given amount of SQUID/SQUILL LP tokens
    @dev Uses the Curve pool's calc_withdraw_one_coin to determine SQUID equivalent
    @param quantity Amount of SQUID/SQUILL LP tokens to convert (defaults to 1 LP token)
    @return SQUID equivalent amount for the given LP token quantity
    """
    return self._squill_lp_equivalent(quantity)


# ============================================================================================
# 👀 Internal Functions
# ============================================================================================

# ======================
# NAKED SQUID 🦑🛀
# ======================

@internal
@view
def _squid_balance(addr: address) -> uint256:
    return staticcall self.squid_token.balanceOf(addr)


# ======================
# SQUID/ETH LP 🦑💎
# ======================

@internal
@view
def _squid_lp_balance(addr: address) -> uint256:
    lp_val: uint256 = staticcall self.squid_eth_lp_token.balanceOf(addr)
    lp_val += staticcall self.squid_eth_gauge.balanceOf(addr)
    lp_val += staticcall self.squid_eth_cvx.balanceOf(addr)
    lp_val += staticcall self.squid_eth_stakedao.balanceOf(addr)
    return lp_val


@internal
@view
def _squid_lp_balance_in_squid(addr: address) -> uint256:
    bal: uint256 = self._squid_lp_balance(addr)
    if bal < 10_000_000:  # Dust protection
        return 0

    rate: uint256 = self._squid_lp_equivalent(bal)
    return bal * rate // 10**18


@internal
@view
def _squid_lp_equivalent(quantity: uint256 = 10**18) -> uint256:
    return self._lp_equivalent(self.squid_eth_pool, 1, quantity)


# ======================
# SQUID/SQUILL LP 🦑🪶
# ======================

@internal
@view
def _squill_lp_balance(addr: address) -> uint256:
    lp_val: uint256 = staticcall self.squill_lp_token.balanceOf(addr)
    lp_val += staticcall self.squill_gauge.balanceOf(addr)
    lp_val += staticcall self.squill_cvx.balanceOf(addr)
    lp_val += staticcall self.squill_stakedao.balanceOf(addr)
    return lp_val


@internal
@view
def _squill_lp_balance_in_squid(addr: address) -> uint256:
    bal: uint256 = self._squill_lp_balance(addr)
    if bal < 10_000_000:  # Dust protection
        return 0

    rate: uint256 = self._squill_lp_equivalent(bal)
    return bal * rate // 10**18


@internal
@view
def _squill_lp_equivalent(quantity: uint256 = 10**18) -> uint256:
    return self._lp_equivalent(self.squill_squid_pool, 0, quantity)


# ======================
# PRICE ORACLES ⚖️
# ======================

@internal
@view
def _eth_usd_price() -> uint256:
    return staticcall self.eth_usd_pool.price_oracle(0)


@internal
@view
def _squid_usd_price() -> uint256:
    _squid_eth_price: uint256 = self._squid_eth_price()
    _eth_usd_price: uint256 = self._eth_usd_price()
    return _squid_eth_price * _eth_usd_price // 10**18


@internal
@view
def _squid_eth_price() -> uint256:
    return staticcall self.squid_eth_pool.price_oracle()


@internal
@view
def _squill_usd_price() -> uint256:
    squill_squid_price: uint256 = (staticcall self.squill_squid_pool.price_oracle())
    squid_usd_price: uint256 = self._squid_usd_price()
    return squill_squid_price * squid_usd_price // 10**18


@internal
@view
def _lp_equivalent(pool: TwoCrypto, index: uint256, quantity: uint256) -> uint256:
    # SQUID index sanity check or burn it all
    assert (staticcall pool.coins(index) == self.squid_token.address)

    # Effective SQUID single-sided withdraw amount
    retval: uint256 = 0
    if quantity > 0:
        _out: uint256 = (staticcall pool.calc_withdraw_one_coin(quantity, index))
        retval = _out * 10**18 // quantity

    return retval
