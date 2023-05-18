from part1_q1 import Address

PREFIX = 'pas'

class VanityAddress(Address):
    def __init__(self, prefix: str, network: Address.Network = Address.Network.TESTNET):
        super().__init__(network)
        self._prefix = prefix
        self._number_of_tries = 0

    def __str__(self):
        return f'{super().__str__()}\n' \
               f'Prefix:            {self.prefix}\n' \
               f'Number of tries:   {self.number_of_tries}'

    @property
    def prefix(self) -> str:
        return self._prefix

    @prefix.setter
    def prefix(self, prefix: str):
        self._prefix = prefix

    @property
    def number_of_tries(self) -> int:
        return self._number_of_tries

    def generate(self) -> None:
        while True:
            super().generate()
            self._number_of_tries += 1
            if self.bitcoin_address[1:].startswith(self.prefix):
                break


def main():
    prefix = PREFIX
    address = VanityAddress(prefix)
    address.generate()
    print(address)


if __name__ == '__main__':
    main()
