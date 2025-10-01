import os

import boa
import pytest
from dotenv import load_dotenv

# Fork mode configuration
load_dotenv()
FORK_RPC_URI = f"https://rpc.frax.com"
SQUID_ADDR = "0x6e58089d8E8f664823d26454f49A5A0f2fF697Fe"

@pytest.fixture(scope="session")
def fork_mode(request):
    """Fixture to determine if tests should run against a fork"""
    return request.config.getoption("--fork", default=False)


def pytest_addoption(parser):
    """Add fork option to pytest"""
    parser.addoption("--fork", action="store_true", help="run tests against fork")


def pytest_configure(config):
    """Add custom markers to pytest"""
    config.addinivalue_line(
        "markers", "fork_only: mark test to run only when --fork is used"
    )


def pytest_runtest_setup(item):
    """Skip fork_only marks when not in fork mode"""
    if "fork_only" in item.keywords and not item.config.getoption("--fork"):
        pytest.skip("test requires fork network")


@pytest.fixture(scope="session")
def zero_address():
    return "0x0000000000000000000000000000000000000000"


@pytest.fixture
def squid(env, fork_mode, zero_address):
    if fork_mode:
        token = boa.load_partial("contracts/test/ERC20.vy")
        return token.at(SQUID_ADDR)
    else:
        return zero_address


@pytest.fixture(scope="session")
def env(fork_mode):
    """Set up the boa environment based on fork mode"""
    if fork_mode:
        boa.fork(FORK_RPC_URI, allow_dirty=True)
    return boa.env



@pytest.fixture(scope="session")
def census(env, fork_mode):
    contract = boa.load_partial("contracts/SquidDaoVote.vy")
    deployment = contract.deploy()
    return deployment


@pytest.fixture(scope="session")
def voter_addresses(zero_address):
    return [
        "0x5abC63ebF1950d531408cf8E12cE24c047504847",  # Voter with raw squid and squid_squill ZERO
        "0xb19d6b66b18fae0fca1023138b229e5f970b5180",  # Voter with raw squid, lp, and squid_squill PMM
        "0x6c46f3f23ed4a070da8d7c1af302d09394efb79f",  # Voter with raw squid and lp, no squid_squill
        "0x02feb744ca516fd6e41d940ae2d0f7cb6fcb1ac3",  # Just squid
        "0x1525D8fcAD680088245055fFB43179367D3EFfC0",  # Squid/ETH Dust address
        "0xda1d9534BeF3344Fa5be3B644b767b349e7415C7",  # Squid/ETH Gauge dust addr
        "0xB5B56FCdf374cdAB0cEAE4bB75844d2a6E59d4D7",  # Stake DAO sqSQUILL
        "0xfC4B2a62A06cb2E1C6A743E9aE327Bb16977E4c1",  # SquidETH Stake DAO > 1
        "0x40d2Ce4C14f04bD91c59c6A1CD6e28F2A0fc81F8",  # SquidETH Stake DAO < 1
        zero_address,
    ]

