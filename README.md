# EPQ Cryptocurrency Artefact

## Running the Programme

### 1. Install Python https://www.python.org/downloads/
### 2. Create virtual enviroment
 Unix/Linux
```bash
python3 -m venv .venv
```
 Windows
```powershell
python -m venv .venv
```
### 3. Activate virtual enviroment

Unix/Linux
```bash
source ./.venv/bin/activate
```
 Windows
```powershell
.\.venv\Scripts\activate
```
### 4. Install packages
```bash
pip install -r requirements.txt
```
### 5. Run main.py
```bash
python ./crypto_currency/main.py
```

## Settings
- host e.g. "0.0.0.0" or "localhost"
- port e.g. 3758 or 14065
- bootstrap e.g. ("host", port)
- verbose e.g. 1, 2 or 3
- log_file e.g. /var/log/crypto.log
- max_connections e.g. 100, 4, 0
- blockchan e.g. blockchain.db
- api e.g. True or False (only be true if miner is False vice versa)
- web_port e.g. 4793, 8080
- miner e.g. True or False
- miner_addr e.g. address for coinbase