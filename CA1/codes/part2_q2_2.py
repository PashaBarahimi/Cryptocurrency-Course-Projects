import bitcoin
import bitcoin.wallet
from bitcoin.core.script import (
    OP_0,
    OP_CHECKMULTISIG,
    SIGHASH_ALL,
    CScript,
    SignatureHash,
)

from transaction import Destination, Transaction, UnspentTransactionOutput


def multi_sig_2_of_3(pub1: bytes, pub2: bytes, pub3: bytes) -> CScript:
    return CScript([2, pub1, pub2, pub3, 3, OP_CHECKMULTISIG])  # type: ignore


def sig_script_2_of_3(sig1: bytes, sig2: bytes) -> CScript:
    return CScript([OP_0, sig1, sig2])  # type: ignore


def sign(
    tx: Transaction, utxo_index: int, private_key: bitcoin.wallet.CBitcoinSecret
) -> bytes:
    txin_script_pub_key = tx._utxos[utxo_index].script_pub_key
    sighash = SignatureHash(txin_script_pub_key, tx._tx, 0, SIGHASH_ALL)
    return private_key.sign(sighash) + bytes([SIGHASH_ALL])  # type: ignore


def main():
    private_key = "92Zh9ENA7DeNBr3FXa1QMLi4igPAzUKy44TEPMW7rogBtGz4CaR"

    bitcoin.SelectParams("testnet")
    private_key1 = bitcoin.wallet.CBitcoinSecret(
        "93RdsGKJn6ExkLEWpVogpC5kRibgoJDWZWUzjonohYhynkScHLX"
    )
    public_key1 = private_key1.pub
    private_key2 = bitcoin.wallet.CBitcoinSecret(
        "938zdHuD6PVuUb26s31xevjTBPY6fggvrxv9fhJz5UGeAfqF61j"
    )
    public_key2 = private_key2.pub
    private_key3 = bitcoin.wallet.CBitcoinSecret(
        "91cxgQtoYrMLUcDi3PsRvQnPQa9hgx9jc3keaq3vNXzmiaBFBrW"
    )
    public_key3 = private_key3.pub

    tx = Transaction(private_key)

    tx.add_destination(Destination(tx.address, 0.0074))
    tx.add_utxo(
        UnspentTransactionOutput(
            "6c9cea1530ef89838e551bf08481ba4193be9f0ed9d8dcdcceff20a645f9e357",
            0,
            multi_sig_2_of_3(public_key1, public_key2, public_key3),
        )
    )

    tx._create_transaction()

    sig1 = sign(tx, 0, private_key1)
    sig2 = sign(tx, 0, private_key2)
    tx._utxos[0]._custom_sig = sig_script_2_of_3(sig1, sig2)

    resp = tx.create()
    print(f"[{resp.status_code}] {resp.reason}")
    print(resp.text)


if __name__ == "__main__":
    main()
