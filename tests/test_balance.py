import time

import boa
import pytest
import requests

pytestmark = pytest.mark.fork_only

# Global cache for CoinGecko prices to avoid multiple API calls
_coingecko_prices_cache = None


def fetch_coingecko_prices():
    """
    Fetch current prices from CoinGecko API for all required tokens in a single call.
    Returns a dict with slug -> price mapping or None if there's an error.
    This function caches the results globally for the entire test session.
    """
    global _coingecko_prices_cache

    # Return cached prices if available
    if _coingecko_prices_cache is not None:
        return _coingecko_prices_cache

    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "ethereum,leviathan-points,squill", "vs_currencies": "usd"}
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Cache the results globally
        _coingecko_prices_cache = data
        print(
            f"Cached CoinGecko prices: ETH=${data.get('ethereum', {}).get('usd', 'N/A')}, "
            f"SQUID=${data.get('leviathan-points', {}).get('usd', 'N/A')}, "
            f"SQUILL=${data.get('squill', {}).get('usd', 'N/A')}"
        )
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching prices from CoinGecko: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching prices from CoinGecko: {e}")
        return None
    finally:
        # Respectful delay to avoid rate limits
        time.sleep(1)


def get_coingecko_price(slug):
    """
    Get price for a specific slug from the cached CoinGecko data.
    """
    prices = fetch_coingecko_prices()
    if prices and slug in prices and "usd" in prices[slug]:
        return prices[slug]["usd"]
    else:
        print(f"Warning: Could not find price data for {slug}")
        return None


def get_cached_prices():
    """
    Get all cached prices for use in LP equivalency calculations.
    Returns a dict with 'eth', 'squid', 'squill' keys.
    """
    prices = fetch_coingecko_prices()
    if not prices:
        return None

    return {
        "eth": prices.get("ethereum", {}).get("usd"),
        "squid": prices.get("leviathan-points", {}).get("usd"),
        "squill": prices.get("squill", {}).get("usd"),
    }


def test_voter_has_balance(voter_addresses, squid, census):
    raw_squid = [False, False]
    lp_bal_test = [False, False]
    pro_quo_bal = [False, False]

    for voter in voter_addresses:
        bal = squid.balanceOf(voter)
        if bal == 0:
            raw_squid[0] = True
        elif bal > 0:
            raw_squid[1] = True

        lp_bal = census.squid_lp_balance(voter)
        if lp_bal == 0:
            lp_bal_test[0] = True
        elif lp_bal > 0:
            lp_bal_test[1] = True

        squid_squill_bal = census.squill_lp_balance(voter)
        if squid_squill_bal == 0:
            pro_quo_bal[0] = True
        else:
            pro_quo_bal[1] = True
    assert raw_squid == [True, True]
    assert lp_bal_test == [True, True]
    assert pro_quo_bal == [True, True]


def test_census_returns_balance(voter_addresses, census, zero_address):
    for voter in voter_addresses:
        bal = census.balanceOf(voter)
        if voter == zero_address:
            assert bal == 0
        else:
            assert bal > 0


def test_eth_price(census):
    eth_price = census.eth_price() / 10**18
    coingecko_eth_price = get_coingecko_price("ethereum")

    assert coingecko_eth_price is not None, "Failed to fetch ETH price from CoinGecko"

    # Allow for some variance (±5%) between contract price and CoinGecko price
    price_variance = abs(eth_price - coingecko_eth_price) / coingecko_eth_price
    assert (
        price_variance < 0.05
    ), f"ETH price variance too high: contract={eth_price}, coingecko={coingecko_eth_price}, variance={price_variance:.2%}"


def test_squid_price(census):
    squid_price = census.squid_price() / 10**18
    coingecko_squid_price = get_coingecko_price("leviathan-points")

    assert (
        coingecko_squid_price is not None
    ), "Failed to fetch SQUID price from CoinGecko"

    # Allow for some variance (±10%) between contract price and CoinGecko price
    price_variance = abs(squid_price - coingecko_squid_price) / coingecko_squid_price
    assert (
        price_variance < 0.10
    ), f"SQUID price variance too high: contract={squid_price}, coingecko={coingecko_squid_price}, variance={price_variance:.2%}"


def test_squill_price(census):
    squill_price = census.squill_price() / 10**18
    coingecko_squill_price = get_coingecko_price("squill")

    assert (
        coingecko_squill_price is not None
    ), "Failed to fetch SQUILL price from CoinGecko"

    # Allow for some variance (±10%) between contract price and CoinGecko price
    price_variance = abs(squill_price - coingecko_squill_price) / coingecko_squill_price
    assert (
        price_variance < 0.10
    ), f"SQUILL price variance too high: contract={squill_price}, coingecko={coingecko_squill_price}, variance={price_variance:.2%}"


def test_squid_lp_equiv(census):
    """
    Test SQUID LP equivalency using cached CoinGecko prices.
    SQUID_LP pool: 50% SQUID + 50% ETH (by USD value)
    Each LP token should contain approximately 1513 SQUID tokens + equivalent ETH.
    """
    squid_val = census.squid_lp_equivalent() / 10**18
    cached_prices = get_cached_prices()

    assert cached_prices is not None, "Failed to fetch cached prices"
    assert cached_prices["squid"] is not None, "SQUID price not available"
    assert cached_prices["eth"] is not None, "ETH price not available"

    # Calculate LP token value based on 50:50 composition
    squid_price_usd = cached_prices["squid"]
    eth_price_usd = cached_prices["eth"]

    # SQUID portion value
    squid_portion_value = squid_val * squid_price_usd

    # ETH portion should equal SQUID portion (50:50 split)
    eth_portion_value = squid_portion_value

    # Total LP token value
    total_lp_value = squid_portion_value + eth_portion_value

    # Expected range: Allow ±15% variance for price fluctuations
    expected_min = total_lp_value * 0.85
    expected_max = total_lp_value * 1.15

    assert (
        total_lp_value > expected_min
    ), f"SQUID LP value too low: ${total_lp_value:.4f} (expected > ${expected_min:.4f})"
    assert (
        total_lp_value < expected_max
    ), f"SQUID LP value too high: ${total_lp_value:.4f} (expected < ${expected_max:.4f})"

    print(
        f"SQUID LP equivalency: {squid_val:.0f} SQUID tokens = ${total_lp_value:.4f} USD"
    )
    print(f"  SQUID portion: ${squid_portion_value:.4f} (50%)")
    print(f"  ETH portion: ${eth_portion_value:.4f} (50%)")
    print(f"  ETH tokens: {eth_portion_value / eth_price_usd:.6f} ETH")


def test_squill_lp_equiv(census):
    """
    Test SQUILL LP equivalency using cached CoinGecko prices.
    SQUILL_LP pool: 50% SQUILL + 50% ETH (by USD value)
    Each LP token should contain approximately 12.63 SQUILL tokens + equivalent ETH.
    """
    squill_val = census.squill_lp_equivalent() / 10**18
    cached_prices = get_cached_prices()

    assert cached_prices is not None, "Failed to fetch cached prices"
    assert cached_prices["squill"] is not None, "SQUILL price not available"
    assert cached_prices["eth"] is not None, "ETH price not available"

    # Calculate LP token value based on 50:50 composition
    squill_price_usd = cached_prices["squill"]
    eth_price_usd = cached_prices["eth"]

    # SQUILL portion value
    squill_portion_value = squill_val * squill_price_usd

    # ETH portion should equal SQUILL portion (50:50 split)
    eth_portion_value = squill_portion_value

    # Total LP token value
    total_lp_value = squill_portion_value + eth_portion_value

    # Expected range: Allow ±15% variance for price fluctuations
    expected_min = total_lp_value * 0.85
    expected_max = total_lp_value * 1.15

    assert (
        total_lp_value > expected_min
    ), f"SQUILL LP value too low: ${total_lp_value:.4f} (expected > ${expected_min:.4f})"
    assert (
        total_lp_value < expected_max
    ), f"SQUILL LP value too high: ${total_lp_value:.4f} (expected < ${expected_max:.4f})"

    print(
        f"SQUILL LP equivalency: {squill_val:.2f} SQUILL tokens = ${total_lp_value:.4f} USD"
    )
    print(f"  SQUILL portion: ${squill_portion_value:.4f} (50%)")
    print(f"  ETH portion: ${eth_portion_value:.4f} (50%)")
    print(f"  ETH tokens: {eth_portion_value / eth_price_usd:.6f} ETH")
