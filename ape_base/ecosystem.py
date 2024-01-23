from typing import ClassVar, Dict, Tuple, Type, cast

from ape.api import TransactionAPI
from ape.types import TransactionSignature
from ape_ethereum.ecosystem import (
    BaseEthereumConfig,
    Ethereum,
    NetworkConfig,
    create_network_config,
)
from ape_ethereum.transactions import (
    AccessListTransaction,
    DynamicFeeTransaction,
    StaticFeeTransaction,
    TransactionType,
)

NETWORKS = {
    # chain_id, network_id
    "mainnet": (8453, 8453),
    "goerli": (84531, 84531),
    "sepolia": (84532, 84532),
}
_SECOND_STATIC_TYPE = 126


def _create_config() -> NetworkConfig:
    return create_network_config(
        block_time=2, required_confirmations=1, default_transaction_type=TransactionType.STATIC
    )


class BaseConfig(BaseEthereumConfig):
    DEFAULT_TRANSACTION_TYPE: ClassVar[int] = TransactionType.STATIC.value
    NETWORKS: ClassVar[Dict[str, Tuple[int, int]]] = NETWORKS
    mainnet: NetworkConfig = _create_config()
    goerli: NetworkConfig = _create_config()
    sepolia: NetworkConfig = _create_config()


class Base(Ethereum):
    @property
    def config(self) -> BaseConfig:  # type: ignore
        return cast(BaseConfig, self.config_manager.get_config("base"))

    def create_transaction(self, **kwargs) -> TransactionAPI:
        """
        Returns a transaction using the given constructor kwargs.
        Overridden because does not support

        **kwargs: Kwargs for the transaction class.

        Returns:
            :class:`~ape.api.transactions.TransactionAPI`
        """

        # Handle all aliases.
        tx_data = dict(kwargs)
        tx_data = _correct_key(
            "max_priority_fee",
            tx_data,
            ("max_priority_fee_per_gas", "maxPriorityFeePerGas", "maxPriorityFee"),
        )
        tx_data = _correct_key("max_fee", tx_data, ("max_fee_per_gas", "maxFeePerGas", "maxFee"))
        tx_data = _correct_key("gas", tx_data, ("gas_limit", "gasLimit"))
        tx_data = _correct_key("gas_price", tx_data, ("gasPrice",))
        tx_data = _correct_key(
            "type",
            tx_data,
            ("txType", "tx_type", "txnType", "txn_type", "transactionType", "transaction_type"),
        )

        # Handle unique value specifications, such as "1 ether".
        if "value" in tx_data and not isinstance(tx_data["value"], int):
            value = tx_data["value"] or 0  # Convert None to 0.
            tx_data["value"] = self.conversion_manager.convert(value, int)

        # None is not allowed, the user likely means `b""`.
        if "data" in tx_data and tx_data["data"] is None:
            tx_data["data"] = b""

        # Deduce the transaction type.
        transaction_types: Dict[int, Type[TransactionAPI]] = {
            TransactionType.STATIC.value: StaticFeeTransaction,
            TransactionType.DYNAMIC.value: DynamicFeeTransaction,
            TransactionType.ACCESS_LIST.value: AccessListTransaction,
            _SECOND_STATIC_TYPE: StaticFeeTransaction,
        }

        if "type" in tx_data:
            if tx_data["type"] is None:
                # Explicit `None` means used default.
                version = self.default_transaction_type.value
            elif isinstance(tx_data["type"], TransactionType):
                version = tx_data["type"].value
            elif isinstance(tx_data["type"], int):
                version = tx_data["type"]
            else:
                # Using hex values or alike.
                version = self.conversion_manager.convert(tx_data["type"], int)

        elif "gas_price" in tx_data:
            version = TransactionType.STATIC.value
        elif "max_fee" in tx_data or "max_priority_fee" in tx_data:
            version = TransactionType.DYNAMIC.value
        elif "access_list" in tx_data or "accessList" in tx_data:
            version = TransactionType.ACCESS_LIST.value
        else:
            version = self.default_transaction_type.value

        tx_data["type"] = version

        # This causes problems in pydantic for some reason.
        # NOTE: This must happen after deducing the tx type!
        if "gas_price" in tx_data and tx_data["gas_price"] is None:
            del tx_data["gas_price"]

        txn_class = transaction_types[version]

        if "required_confirmations" not in tx_data or tx_data["required_confirmations"] is None:
            # Attempt to use default required-confirmations from `ape-config.yaml`.
            required_confirmations = 0
            active_provider = self.network_manager.active_provider
            if active_provider:
                required_confirmations = active_provider.network.required_confirmations

            tx_data["required_confirmations"] = required_confirmations

        if isinstance(tx_data.get("chainId"), str):
            tx_data["chainId"] = int(tx_data["chainId"], 16)

        elif (
            "chainId" not in tx_data or tx_data["chainId"] is None
        ) and self.network_manager.active_provider is not None:
            tx_data["chainId"] = self.provider.chain_id

        if "input" in tx_data:
            tx_data["data"] = tx_data.pop("input")

        if all(field in tx_data for field in ("v", "r", "s")):
            tx_data["signature"] = TransactionSignature(
                v=tx_data["v"],
                r=bytes(tx_data["r"]),
                s=bytes(tx_data["s"]),
            )

        if "gas" not in tx_data:
            tx_data["gas"] = None

        return txn_class(**tx_data)


def _correct_key(key: str, data: Dict, alt_keys: Tuple[str, ...]) -> Dict:
    if key in data:
        return data

    # Check for alternative.
    for possible_key in alt_keys:
        if possible_key not in data:
            continue

        # Alt found: use it.
        new_data = {k: v for k, v in data.items() if k not in alt_keys}
        new_data[key] = data[possible_key]
        return new_data

    return data
