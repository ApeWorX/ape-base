from ape_ethereum.transactions import TransactionType

from ape_blast.ecosystem import BlastConfig


def test_gas_limit(blast):
    assert blast.config.local.gas_limit == "max"


def test_default_transaction_type(blast):
    assert blast.config.mainnet.default_transaction_type == TransactionType.STATIC


def test_mainnet_fork_not_configured():
    obj = BlastConfig.model_validate({})
    assert obj.mainnet_fork.required_confirmations == 0


def test_mainnet_fork_configured():
    data = {"mainnet_fork": {"required_confirmations": 555}}
    obj = BlastConfig.model_validate(data)
    assert obj.mainnet_fork.required_confirmations == 555


def test_custom_network():
    data = {"apenet": {"required_confirmations": 333}}
    obj = BlastConfig.model_validate(data)
    assert obj.apenet.required_confirmations == 333
