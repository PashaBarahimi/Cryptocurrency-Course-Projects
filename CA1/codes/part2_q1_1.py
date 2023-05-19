from bitcoin.core.script import OP_CHECKSIG, OP_RETURN, CScript

from transaction import Destination, Transaction, UnspentTransactionOutput

UNSPENDABLE_SCRIPT_PUB_KEY = CScript([OP_RETURN])  # type: ignore
SPENDABLE_BY_ANYONE_SCRIPT_PUB_KEY = CScript([OP_CHECKSIG])  # type: ignore


def main():
    private_key = "92Zh9ENA7DeNBr3FXa1QMLi4igPAzUKy44TEPMW7rogBtGz4CaR"

    tx = Transaction(private_key)
    tx.add_destination(Destination(tx.address, 0.002, UNSPENDABLE_SCRIPT_PUB_KEY))
    tx.add_destination(
        Destination(tx.address, 0.008, SPENDABLE_BY_ANYONE_SCRIPT_PUB_KEY)
    )
    tx.add_utxo(
        UnspentTransactionOutput(
            "12a4ccff3ed9bec0715fcf678b914397e1e7b3fcea239fe551f269c89810f909",
            0,
            tx.my_P2PKH_script_pub_key(),
        )
    )

    resp = tx.create()
    print(f"[{resp.status_code}] {resp.reason}")
    print(resp.text)


if __name__ == "__main__":
    main()
