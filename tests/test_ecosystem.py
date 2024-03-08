import pytest
from ape_ethereum.transactions import TransactionType
from ethpm_types import MethodABI

from ape_blast.ecosystem import _SECOND_STATIC_TYPE


@pytest.mark.parametrize(
    "tx_kwargs",
    [
        {},
        {"type": 0},
        {"gas_price": 0},
        {"gasPrice": 0},
    ],
)
def test_create_transaction_type_0(blast, tx_kwargs):
    txn = blast.create_transaction(**tx_kwargs)
    assert txn.type == TransactionType.STATIC.value


@pytest.mark.parametrize(
    "tx_kwargs",
    [
        {"type": 2},
        {"max_fee": 0},
        {"max_fee_per_gas": 0},
        {"maxFee": 0},
        {"max_priority_fee_per_gas": 0},
        {"max_priority_fee": 0},
        {"maxPriorityFeePerGas": 0},
    ],
)
def test_create_transaction_type_2(blast, tx_kwargs):
    """
    Show is smart-enough to deduce type 2 transactions.
    """

    txn = blast.create_transaction(**tx_kwargs)
    assert txn.type == TransactionType.DYNAMIC.value


@pytest.mark.parametrize(
    "tx_type",
    (TransactionType.STATIC.value, TransactionType.DYNAMIC.value, _SECOND_STATIC_TYPE),
)
def test_encode_transaction(tx_type, blast, eth_tester_provider):
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
    actual = blast.encode_transaction(address, abi, sender=address, type=tx_type)
    assert actual.gas_limit == eth_tester_provider.max_gas
