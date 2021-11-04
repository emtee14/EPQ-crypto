# EPQ Cryptocurrency Artefact


## SQL Schema

### Transactions

- sender: str
- receiver: str
- value: int
- data: str
- fee: int
- signature: str
- nonce: int
- parent_block: str

### Blocks

- hash: str
- nonce: int
- coinbase: str
- parent_block: str
- timestamp: int
- transactions: List (Joined from `transactions` table)
