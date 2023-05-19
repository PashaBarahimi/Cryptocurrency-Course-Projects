from bitcoin.core.script import OP_CHECKSIG, CScript

from transaction import Destination, Transaction, UnspentTransactionOutput

SPENDABLE_BY_ANYONE_SCRIPT_PUB_KEY = CScript([OP_CHECKSIG])  # type: ignore


def main():
    private_key = "92Zh9ENA7DeNBr3FXa1QMLi4igPAzUKy44TEPMW7rogBtGz4CaR"

    tx = Transaction(private_key)
    tx.add_destination(Destination("mu2XGdXpAM8fkFMWksFmMqCYP6oUXTVxRs", 0.0078))
    tx.add_utxo(
        UnspentTransactionOutput(
            "76d3ef0f1c733e5b6a15da0233ceca7a5694674cf3f511c6015fdc3d7f52b00a",
            1,
            SPENDABLE_BY_ANYONE_SCRIPT_PUB_KEY,
        )
    )

    resp = tx.create()
    print(f"[{resp.status_code}] {resp.reason}")
    print(resp.text)


if __name__ == "__main__":
    main()
