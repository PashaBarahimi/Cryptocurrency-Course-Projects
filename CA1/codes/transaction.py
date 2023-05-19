import enum

import base58
import bitcoin.wallet
import requests
from bitcoin.core import (
    COIN,
    CMutableTransaction,
    CMutableTxIn,
    CMutableTxOut,
    COutPoint,
    Hash160,
    b2x,
    lx,
)
from bitcoin.core.script import *
from bitcoin.core.scripteval import SCRIPT_VERIFY_P2SH, VerifyScript

TRANSACTION_BROADCAST_URL = "https://api.blockcypher.com/v1/btc/test3/txs/push"


def address_to_pub_key_hash160(address: str) -> bytes:
    pub_key_hash = base58.b58decode_check(address)[1:]
    return pub_key_hash


def P2PKH_script_pub_key(pub_key_hash: bytes) -> CScript:
    return CScript([OP_DUP, OP_HASH160, pub_key_hash, OP_EQUALVERIFY, OP_CHECKSIG])  # type: ignore


class Destination:
    def __init__(
        self, address: str, amount: float, script_pub_key: CScript | None = None
    ):
        self._address = address
        self._script_pub_key = (
            P2PKH_script_pub_key(address_to_pub_key_hash160(address))
            if script_pub_key is None
            else script_pub_key
        )
        self._amount = amount

    @property
    def address(self) -> str:
        return self._address

    @property
    def script_pub_key(self) -> CScript:
        return self._script_pub_key

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def TxOut(self) -> CMutableTxOut:
        return CMutableTxOut(int(self.amount * COIN), self.script_pub_key)


class UnspentTransactionOutput:
    def __init__(
        self,
        tx_id: str,
        index: int,
        script_pub_key: CScript,
        custom_sig: CScript | None = None,
    ):
        self._tx_id = tx_id
        self._index = index
        self._script_pub_key = script_pub_key
        self._custom_sig = custom_sig

    @property
    def tx_id(self) -> str:
        return self._tx_id

    @property
    def index(self) -> int:
        return self._index

    @property
    def script_pub_key(self) -> CScript:
        return self._script_pub_key

    @property
    def custom_sig(self) -> CScript | None:
        return self._custom_sig

    @property
    def TxIn(self) -> CMutableTxIn:
        return CMutableTxIn(COutPoint(lx(self.tx_id), self.index))


class Transaction:
    class Network(enum.Enum):
        MAINNET = "mainnet"
        TESTNET = "testnet"

    def __init__(self, private_key: str, network: Network = Network.TESTNET):
        self._network = network
        bitcoin.SelectParams(self._network.value)

        self._private_key = bitcoin.wallet.CBitcoinSecret(private_key)
        self._public_key = self._private_key.pub
        self._address = bitcoin.wallet.P2PKHBitcoinAddress.from_pubkey(self._public_key)
        self._destinations = []
        self._utxos = []
        self._tx = CMutableTransaction()

    @property
    def address(self) -> str:
        return str(self._address)

    def add_destination(self, destinations: Destination) -> None:
        self._destinations.append(destinations)

    def add_utxo(self, utxos: UnspentTransactionOutput) -> None:
        self._utxos.append(utxos)

    def create(self) -> requests.Response:
        if not self._destinations:
            raise ValueError("No destinations were added to the transaction")
        if not self._utxos:
            raise ValueError(
                "No unspent transaction outputs were added to the transaction"
            )
        self._create_transaction()
        self._verify()
        return self._broadcast_transaction()

    def my_P2PKH_script_pub_key(self) -> CScript:
        return P2PKH_script_pub_key(Hash160(self._public_key))

    def _my_P2PKH_script_sig(self, txin_script_pub_key: CScript) -> CScript:
        signature = self._create_OP_CHECKSIG_signature(txin_script_pub_key)
        return CScript([signature, self._public_key])  # type: ignore

    def _create_transaction(self) -> None:
        txins = [utxo.TxIn for utxo in self._utxos]
        txouts = [destination.TxOut for destination in self._destinations]
        self._tx = CMutableTransaction(txins, txouts)

    def _create_OP_CHECKSIG_signature(self, txin_script_pub_key: CScript) -> bytes:
        sighash = SignatureHash(txin_script_pub_key, self._tx, 0, SIGHASH_ALL)
        sig = self._private_key.sign(sighash) + bytes([SIGHASH_ALL])  # type: ignore
        return sig

    def _verify(self):
        for i, _ in enumerate(self._utxos):
            txin_script_pub_key = self._utxos[i].script_pub_key
            txin_script_sig = self._utxos[i].custom_sig
            if txin_script_sig is None:
                txin_script_sig = self._my_P2PKH_script_sig(txin_script_pub_key)
            self._tx.vin[i].scriptSig = txin_script_sig
            VerifyScript(
                self._tx.vin[i].scriptSig,
                txin_script_pub_key,
                self._tx,
                i,
                (SCRIPT_VERIFY_P2SH,),
            )

    def _broadcast_transaction(self) -> requests.Response:
        raw_transaction = b2x(self._tx.serialize())
        headers = {"content-type": "application/x-www-form-urlencoded"}
        return requests.post(
            TRANSACTION_BROADCAST_URL,
            headers=headers,
            data='{"tx": "%s"}' % raw_transaction,
            timeout=60,
        )
