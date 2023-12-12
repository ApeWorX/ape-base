import pytest
from ape_ethereum.transactions import TransactionType
from ethpm_types import MethodABI

from ape_base.ecosystem import _SECOND_STATIC_TYPE


def test_gas_limit(base, eth_tester_provider):
    assert base.config.local.gas_limit == "max"


# NOTE: None because we want to show the default is STATIC
@pytest.mark.parametrize("tx_type", (None, 0, "0x0"))
def test_create_transaction(base, tx_type, eth_tester_provider):
    tx = base.create_transaction(type=tx_type)
    assert tx.type == TransactionType.STATIC.value
    assert tx.gas_limit == eth_tester_provider.max_gas


@pytest.mark.parametrize(
    "tx_type",
    (TransactionType.STATIC.value, TransactionType.DYNAMIC.value, _SECOND_STATIC_TYPE),
)
def test_encode_transaction(tx_type, base, eth_tester_provider):
    abi = MethodABI.model_validate(
        {
            "type": "function",
            "name": "fooAndBar",
            "stateMutability": "nonpayable",
            "inputs": [],
            "outputs": [],
        }
    )
    address = "0x274b028b03A250cA03644E6c578D81f019eE1323"
    actual = base.encode_transaction(address, abi, sender=address, type=tx_type)
    assert actual.gas_limit == eth_tester_provider.max_gas
