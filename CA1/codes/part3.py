import struct
import time

from bitcoin.core import CMutableTransaction, CScript, Hash, b2lx, b2x
from requests import Response

from transaction import Destination, Transaction, UnspentTransactionOutput

BITCOIN_MINE_AWARD = 6.25


class BaseCoinTransaction(Transaction):
    def __init__(
        self,
        private_key: str,
        data: str,
        network: Transaction.Network = Transaction.Network.MAINNET,
    ):
        super().__init__(private_key, network)
        self._data = data

        self._destinations.append(Destination(self.address, BITCOIN_MINE_AWARD))
        self._utxos.append(UnspentTransactionOutput("0" * 64, 0xFFFFFFFF, CScript([]), self._get_coinbase_sig()))  # type: ignore

    def _get_coinbase_sig(self) -> CScript:
        hex_data = self._data.encode("utf-8").hex()
        return CScript([bytes.fromhex(hex_data)])  # type: ignore

    def create(self) -> CMutableTransaction:
        self._create_transaction()
        self._tx.vin[0].scriptSig = self._utxos[0].custom_sig
        return self._tx

    def _broadcast_transaction(self) -> Response:
        raise NotImplementedError("BaseCoinTransaction cannot be broadcasted")

    def _verify(self) -> None:
        raise NotImplementedError("BaseCoinTransaction cannot be verified")


class BitcoinBlock:
    def __init__(
        self,
        transactions: list[CMutableTransaction],
        prev_block_hash: str,
        bits: str = "0x1f010000",
        timespamp: int = int(time.time()),
    ):
        self._transactions = transactions
        self._prev_block_hash = prev_block_hash
        self._merkle_root = self._calculate_merkle_root()
        self._timestamp = timespamp
        self._bits = int(bits, 16)
        self._target = self._get_target(bits)
        self._version = 2
        self._nonce = 0
        self._partial_header = self._get_partial_header()
        self._header = self._partial_header
        self._body = self._get_body()

    @property
    def header(self) -> bytes:
        return self._header

    @property
    def body(self) -> bytes:
        return self._body

    @property
    def nonce(self) -> int:
        return self._nonce

    @property
    def version(self) -> int:
        return self._version

    @property
    def target(self) -> str:
        return "0x" + self._target.hex()

    @property
    def merkle_root(self) -> str:
        return self._merkle_root

    @property
    def block(self) -> bytes:
        magic_number = 0xD9B4BEF9.to_bytes(4, "little")
        header = self._header
        transaction_counter = len(self._transactions).to_bytes(1, "little")
        body = self._body
        block_size = len(header) + len(transaction_counter) + len(body)
        return (
            magic_number
            + struct.pack("<L", block_size)
            + header
            + transaction_counter
            + body
        )

    def _calculate_merkle_root(self) -> str:
        hashes = [Hash(tx.serialize()) for tx in self._transactions]
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            hashes = [
                Hash(hash1 + hash2) for hash1, hash2 in zip(hashes[::2], hashes[1::2])
            ]
        return b2lx(hashes[0])

    @staticmethod
    def _get_target(bits: str) -> bytes:
        exponent = bits[2:4]
        coefficient = bits[4:]
        target = int(coefficient, 16) * 2 ** (8 * (int(exponent, 16) - 3))
        target_hex = hex(target)[2:]
        return bytes.fromhex(target_hex.zfill(64))

    def _get_hash_value(self) -> bytes:
        nonce = struct.pack("<L", self._nonce)
        self._header = self._partial_header + nonce
        return Hash(self._header)

    def _get_partial_header(self) -> bytes:
        return (
            struct.pack("<L", self._version)
            + bytes.fromhex(self._prev_block_hash)[::-1]
            + bytes.fromhex(self._merkle_root)[::-1]
            + struct.pack("<LL", self._timestamp, self._bits)
        )

    def _get_body(self) -> bytes:
        return b"".join(tx.serialize() for tx in self._transactions)

    def _print_hash_rate(self, start: float, end: bool = False) -> None:
        elapsed_time = time.time() - start
        rate = self._nonce / elapsed_time
        if rate < 1e3:
            unit = "H/s"
        elif rate < 1e6:
            rate /= 1e3
            unit = "KH/s"
        elif rate < 1e9:
            rate /= 1e6
            unit = "MH/s"
        else:
            rate /= 1e9
            unit = "GH/s"
        print(f"\r{' ' * 20}\rHash rate: {rate:.2f} {unit}", end="")
        if end:
            print()

    def mine(self) -> bytes:
        start = time.time()
        while self._nonce < 2**32:
            hash_value = self._get_hash_value()
            if hash_value[::-1] < self._target:
                self._print_hash_rate(start, end=True)
                return hash_value
            self._nonce += 1
            if self._nonce % 1000 == 0:
                self._print_hash_rate(start)
        raise ValueError("Nonce overflow")


def main():
    data = "810199385PashaBarahimi"
    private_key = "5JWoEUpPb1BCRMTYUqNNq4L7eEAptfiz9FKsBAj7niAJWaQ6uZJ"
    bits = "0x1f010000"  # 16 bits leading 0s
    timestamp = int(time.time())
    _ = int(input("Enter the previous block number: "))  # unused
    prev_hash = input("Enter the previous block hash: ")

    basecoin = BaseCoinTransaction(private_key, data, Transaction.Network.MAINNET)
    tx = basecoin.create()

    block = BitcoinBlock([tx], prev_hash, bits, timestamp)
    print("Mining...")
    hash_value = block.mine()

    print(f"Block hash:   {b2lx(hash_value)}")
    print(f"Block header: {b2x(block.header)}")
    print(f"Block body:   {b2x(block.body)}")
    print(f"Block hex:    {b2x(block.block)}")

    print(f"Merkle root:  {block.merkle_root}")
    print(f"Nonce:        {block.nonce}")
    print(f"Version:      {block.version}")
    print(f"Timestamp:    {timestamp}")
    print(f"Bits:         {bits}")
    print(f"Target:       {block.target}")


if __name__ == "__main__":
    main()
