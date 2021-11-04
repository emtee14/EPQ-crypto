# EPQ Cryptocurrency Artefact

## Transactions

### SQL Schema
- sender: str
- receiver: str
- value: int
- data: str
- fee: int
- signature: str
- nonce: int
- parent_block: str

## Blocks

### SQL Schema
- hash: str
- nonce: int
- coinbase: str
- parent_block: str
- timestamp: int
- transactions: List (Joined from `transactions` table)