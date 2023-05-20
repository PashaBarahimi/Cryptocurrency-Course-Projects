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
PRIME_NUM1_IN_BYTES = PRIME_NUM1.to_bytes(2, byteorder="little")
PRIME_NUM2 = 881
PRIME_NUM2_IN_BYTES = PRIME_NUM2.to_bytes(2, byteorder="little")

SUM = PRIME_NUM1 + PRIME_NUM2
SUM_IN_BYTES = SUM.to_bytes(2, byteorder="little")
DIFF = PRIME_NUM1 - PRIME_NUM2
DIFF_IN_BYTES = DIFF.to_bytes(1, byteorder="little")

SCRIPT_SUM_DIFF_PUB_KEY = CScript([OP_2DUP, OP_ADD, OP_HASH160, Hash160(SUM_IN_BYTES), OP_EQUALVERIFY, OP_SUB, OP_HASH160, Hash160(DIFF_IN_BYTES), OP_EQUAL])  # type: ignore
SCRIPT_PRIME_NUMS_SIG = CScript([PRIME_NUM1_IN_BYTES, PRIME_NUM2_IN_BYTES])  # type: ignore


def main():
    private_key = "92Zh9ENA7DeNBr3FXa1QMLi4igPAzUKy44TEPMW7rogBtGz4CaR"

    tx = Transaction(private_key)
    tx.add_destination(Destination(tx.address, 0.014))
    tx.add_utxo(
        UnspentTransactionOutput(
            "e2b73c7d033a2f672b65f64c68322aced2bccc4db44e7cd7a355dcf7ba0b2955",
            0,
            SCRIPT_SUM_DIFF_PUB_KEY,
            SCRIPT_PRIME_NUMS_SIG,
        )
    )

    resp = tx.create()
    print(f"[{resp.status_code}] {resp.reason}")
    print(resp.text)


if __name__ == "__main__":
    main()
