from bitcoin.core.script import (
    OP_2DUP,
    OP_ADD,
    OP_EQUAL,
    OP_EQUALVERIFY,
    OP_HASH160,
    OP_SUB,
    CScript,
    Hash160,
)

from transaction import Destination, Transaction, UnspentTransactionOutput

PRIME_NUM1 = 977
PRIME_NUM2 = 881

SUM = PRIME_NUM1 + PRIME_NUM2
SUM_IN_BYTES = SUM.to_bytes(2, byteorder="little")
DIFF = PRIME_NUM1 - PRIME_NUM2
DIFF_IN_BYTES = DIFF.to_bytes(1, byteorder="little")

SCRIPT_SUM_DIFF_PUB_KEY = CScript([OP_2DUP, OP_ADD, OP_HASH160, Hash160(SUM_IN_BYTES), OP_EQUALVERIFY, OP_SUB, OP_HASH160, Hash160(DIFF_IN_BYTES), OP_EQUAL])  # type: ignore


def main():
    private_key = "92Zh9ENA7DeNBr3FXa1QMLi4igPAzUKy44TEPMW7rogBtGz4CaR"

    tx = Transaction(private_key)
    tx.add_destination(Destination(tx.address, 0.015, SCRIPT_SUM_DIFF_PUB_KEY))
    tx.add_utxo(
        UnspentTransactionOutput(
            "6c7b5a4c4551bafd06b8279f4a64c445d4b46245a65a38c31c058468909c36ff",
            1,
            tx.my_P2PKH_script_pub_key(),
        )
    )

    resp = tx.create()
    print(f"[{resp.status_code}] {resp.reason}")
    print(resp.text)


if __name__ == "__main__":
    main()
