import base58
import ecdsa
import enum
import hashlib
import os

class Address:
    class Network(enum.Enum):
        MAINNET = 0
        TESTNET = 1

    def __init__(self, network: Network = Network.TESTNET):
        self.network = network

    def __str__(self):
        return f'Address:           {self.bitcoin_address}\n' \
               f'Private key (WIF): {self.private_key_wif}\n' \
               f'Private key:       {self.private_key}\n' \
               f'Public key:        {self.public_key}'

    @property
    def network(self) -> Network:
        return self._network

    @network.setter
    def network(self, network: Network):
        self._network = network

    @property
    def private_key_wif(self) -> str:
        return self._to_wif(self._private_key)

    @property
    def private_key(self) -> str:
        return self._private_key.hex()

    @property
    def public_key(self) -> str:
        return self._public_key.hex()

    @property
    def bitcoin_address(self) -> str:
        return self._bitcoin_address

    def generate(self):
        self._generate_key_pair()
        self._generate_bitcoin_address()

    def _get_network_byte(self, is_private: bool = True) -> bytes:
        if is_private:
            if self.network == Address.Network.MAINNET:
                return b'\x80'
            elif self.network == Address.Network.TESTNET:
                return b'\xef'
            else:
                raise ValueError('Invalid network')
        elif self.network == Address.Network.MAINNET:
            return b'\x00'
        elif self.network == Address.Network.TESTNET:
            return b'\x6f'
        else:
            raise ValueError('Invalid network')

    def _generate_key_pair(self) -> None:
        private_key = os.urandom(32)
        public_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1).verifying_key

        if public_key is None:
            raise ValueError('Invalid public key')

        self._private_key = private_key
        self._public_key = public_key.to_string()

    def _generate_bitcoin_address(self) -> None:
        sha256 = hashlib.sha256(self._public_key).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256)

        if ripemd160 is None:
            raise ValueError('Invalid ripemd160')

        self._bitcoin_address = self._to_wif(ripemd160.digest(), is_private=False)

    def _to_wif(self, key: bytes, is_private: bool = True) -> str:
        network_byte = self._get_network_byte(is_private)
        key_with_network_byte = network_byte + key
        sha256_1 = hashlib.sha256(key_with_network_byte).digest()
        sha256_2 = hashlib.sha256(sha256_1).digest()
        checksum = sha256_2[:4]
        binary_key = key_with_network_byte + checksum
        wif = base58.b58encode(binary_key).decode('utf-8')
        return wif


def main():
    address = Address(network=Address.Network.TESTNET)
    address.generate()
    print(address)


if __name__ == '__main__':
    main()
