from bitcoin.core.script import OP_CHECKMULTISIG, CScript

from transaction import Destination, Transaction, UnspentTransactionOutput


def multi_sig_2_of_3(pub1: bytes, pub2: bytes, pub3: bytes) -> CScript:
    return CScript([2, pub1, pub2, pub3, 3, OP_CHECKMULTISIG])  # type: ignore


def main():
    private_key = "92Zh9ENA7DeNBr3FXa1QMLi4igPAzUKy44TEPMW7rogBtGz4CaR"

    pub1 = bytes.fromhex(
        "04c9a3dc14a523ad8b6b36f445ce55475e0f716ff0a8e7f92103e36cb344a64a2160c48c2e97a8471537da6154acf6d612d2eae18af07884e25eec1b4dd07a59e9"
    )
    pub2 = bytes.fromhex(
        "04844325ab760b86d29b90a59d88d57ed3ef8b9124b804257ec15d7b4e426400cc74e028f73c949e36b1919aaf823dbc35440538e49151e28ce8c80528f0e0dd21"
    )
    pub3 = bytes.fromhex(
        "048f6a3736d960a861bce581abd4e24f87977dc2804cd3eddec08dbe03804aea562ba30396818f3cf3cfdf0eb0ed8841abb2b3b28510ce89922d275f1f58e707b8"
    )

    tx = Transaction(private_key)
    tx.add_destination(
        Destination(tx.address, 0.0076, multi_sig_2_of_3(pub1, pub2, pub3))
    )
    tx.add_utxo(
        UnspentTransactionOutput(
            "15c794bbb169f272fb1ed45526eef5613a851716a1df574480c12f23126772be",
            0,
            tx.my_P2PKH_script_pub_key(),
        )
    )

    resp = tx.create()
    print(f"[{resp.status_code}] {resp.reason}")
    print(resp.text)


if __name__ == "__main__":
    main()
