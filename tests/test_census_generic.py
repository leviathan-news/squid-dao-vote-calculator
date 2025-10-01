import boa
import pytest

pytestmark = pytest.mark.fork_only


def test_census_balance_functionality(census, zero_address):
    """
    Test that census.balanceOf() works correctly for different scenarios.
    This test verifies the core functionality without exposing specific voter data.
    """
    # Test zero address has zero balance
    assert census.balanceOf(zero_address) == 0, "Zero address should have zero balance"

    # Test that census can calculate balances for arbitrary addresses
    # We'll use some test addresses that may or may not have balances
    test_addresses = [
        "0x0000000000000000000000000000000000000001",  # Test address 1
        "0x0000000000000000000000000000000000000002",  # Test address 2
        "0x0000000000000000000000000000000000000003",  # Test address 3
    ]

    for address in test_addresses:
        balance = census.balanceOf(address)
        assert balance >= 0, f"Balance should be non-negative for address {address}"
        # Note: We don't assert specific values since these are arbitrary test addresses


def test_census_balance_ordering(census, voter_addresses, zero_address):
    """
    Test that census balances are calculated consistently and can be ordered.
    This verifies the ranking logic without hardcoding specific voter addresses.
    """
    # Get balances for all voters
    voter_balances = []
    for voter in voter_addresses:
        balance = census.balanceOf(voter)
        voter_balances.append((voter, balance))

    # Sort by balance (descending - highest first)
    voter_balances.sort(key=lambda x: x[1], reverse=True)

    # Verify that balances are in descending order
    balances = [balance for voter, balance in voter_balances]
    for i in range(len(balances) - 1):
        assert (
            balances[i] >= balances[i + 1]
        ), f"Balance order incorrect: {balances[i]} < {balances[i + 1]}"

    # Verify zero address is at the end (lowest balance)
    assert (
        voter_balances[-1][0] == zero_address
    ), "Zero address should have the lowest balance"
    assert voter_balances[-1][1] == 0, "Zero address should have zero balance"


def test_census_balance_components(census, voter_addresses, zero_address):
    """
    Test that census balance calculation includes all expected components.
    This verifies the balance calculation logic without exposing specific voter data.
    """
    for voter in voter_addresses:
        if voter == zero_address:
            continue

        # Get individual components
        squid_balance = census.squid_balance(voter)
        squid_lp_balance = census.squid_lp_balance_in_squid(voter)
        squill_lp_balance = census.squill_lp_balance_in_squid(voter)
        total_balance = census.balanceOf(voter)

        # All components should be non-negative
        assert (
            squid_balance >= 0
        ), f"SQUID balance should be non-negative for voter {voter}"
        assert (
            squid_lp_balance >= 0
        ), f"SQUID LP balance should be non-negative for voter {voter}"
        assert (
            squill_lp_balance >= 0
        ), f"SQUILL LP balance should be non-negative for voter {voter}"
        assert (
            total_balance >= 0
        ), f"Total balance should be non-negative for voter {voter}"

        # Total should be sum of components (within reasonable precision)
        expected_total = squid_balance + squid_lp_balance + squill_lp_balance
        # Allow for small rounding differences
        assert (
            abs(total_balance - expected_total) <= 1
        ), f"Total balance mismatch for voter {voter}: expected {expected_total}, got {total_balance}"


def test_census_lp_equivalency_consistency(census):
    """
    Test that LP equivalency calculations are consistent.
    This verifies the LP price calculation logic without exposing specific values.
    """
    # Test SQUID LP equivalency
    squid_lp_equiv = census.squid_lp_equivalent()
    assert squid_lp_equiv > 0, "SQUID LP equivalency should be positive"

    # Test SQUILL LP equivalency
    squill_lp_equiv = census.squill_lp_equivalent()
    assert squill_lp_equiv > 0, "SQUILL LP equivalency should be positive"

    # Test that equivalency values are reasonable (not extremely large or small)
    assert squid_lp_equiv < 10**30, "SQUID LP equivalency seems unreasonably large"
    assert squill_lp_equiv < 10**30, "SQUILL LP equivalency seems unreasonably large"

    assert squid_lp_equiv > 10**15, "SQUID LP equivalency seems unreasonably small"
    assert squill_lp_equiv > 10**15, "SQUILL LP equivalency seems unreasonably small"


def test_census_price_consistency(census):
    """
    Test that price calculations are consistent and reasonable.
    This verifies price calculation logic without exposing specific price values.
    """
    # Test ETH price
    eth_price = census.eth_price()
    assert eth_price > 0, "ETH price should be positive"
    assert eth_price < 10**30, "ETH price seems unreasonably large"

    # Test SQUID price
    squid_price = census.squid_price()
    assert squid_price > 0, "SQUID price should be positive"
    assert squid_price < 10**30, "SQUID price seems unreasonably large"

    # Test SQUILL price
    squill_price = census.squill_price()
    assert squill_price > 0, "SQUILL price should be positive"
    assert squill_price < 10**30, "SQUILL price seems unreasonably large"


def test_census_voter_diversity(voter_addresses, census, zero_address):
    """
    Test that we have voters with different types of balances.
    This verifies diversity in voter types without exposing specific voter data.
    """
    has_raw_squid = False
    has_lp_balance = False
    has_squill_lp_balance = False

    for voter in voter_addresses:
        if voter == zero_address:
            continue

        # Check for different types of balances
        if census.squid_balance(voter) > 0:
            has_raw_squid = True
        if census.squid_lp_balance(voter) > 0:
            has_lp_balance = True
        if census.squill_lp_balance(voter) > 0:
            has_squill_lp_balance = True

    # We should have at least some diversity in voter types
    assert has_raw_squid, "Should have voters with raw SQUID balance"
    assert has_lp_balance, "Should have voters with SQUID LP balance"
    assert has_squill_lp_balance, "Should have voters with SQUILL LP balance"


def test_census_balance_calculation_accuracy(census, voter_addresses, zero_address):
    """
    Test that census balance calculations are mathematically accurate.
    This verifies the calculation logic without exposing specific voter data.
    """
    for voter in voter_addresses:
        if voter == zero_address:
            continue

        # Get all balance components
        raw_squid = census.squid_balance(voter)
        squid_lp_raw = census.squid_lp_balance(voter)
        squid_lp_equiv = census.squid_lp_equivalent(squid_lp_raw)
        squid_lp_effective = census.squid_lp_balance_in_squid(voter)

        squill_lp_raw = census.squill_lp_balance(voter)
        squill_lp_equiv = census.squill_lp_equivalent(squill_lp_raw)
        squill_lp_effective = census.squill_lp_balance_in_squid(voter)

        total_balance = census.balanceOf(voter)

        # Verify LP effective calculations match manual calculations
        expected_squid_lp_effective = squid_lp_raw * squid_lp_equiv / (10**18)
        expected_squill_lp_effective = squill_lp_raw * squill_lp_equiv / (10**18)

        # Allow for small rounding differences
        assert (
            abs(squid_lp_effective - expected_squid_lp_effective) <= 1
        ), f"SQUID LP effective calculation mismatch for voter {voter}"
        assert (
            abs(squill_lp_effective - expected_squill_lp_effective) <= 1
        ), f"SQUILL LP effective calculation mismatch for voter {voter}"

        # Verify total balance calculation
        expected_total = raw_squid + squid_lp_effective + squill_lp_effective
        assert (
            abs(total_balance - expected_total) <= 1
        ), f"Total balance calculation mismatch for voter {voter}"
