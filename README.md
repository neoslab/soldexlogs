# SolDexLogs - Solana Log Decoder

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**SolDexLogs** is a real-time Solana log listener and decoder tailored for decentralized exchanges (DEXs). It connects to Solana's mainnet WebSocket endpoint, filters logs from known DEX programs, extracts and decodes base64 data, and stores them in structured JSON Lines format for easy monitoring, analysis, or archival. Ideal for researchers, traders, and developers needing visibility into DEX interactions at the transaction level.

* * *

## Features

- Real-time WebSocket connection to Solana mainnet
- Detects and matches specific DEX program IDs
- Decodes base64 `Program data` entries to hex
- Saves structured logs with timestamp, tx ID, DEX name, and data
- Outputs in newline-delimited JSON (JSONL) format

## Use Cases

- Monitoring live DEX transaction activity
- Analyzing transaction payloads for research or auditing
- Building custom alerting systems for DEX interactions
- Archiving logs for later forensic or compliance review

* * *

### Installation

Clone the repository and install the dependencies (Python 3.10+ recommended):

```bash
git clone https://github.com/yourusername/SolDexLogs.git
cd SolDexLogs
pip install -r requirements.txt
````

Dependencies include:

* `websockets`
* `asyncio`
* `base64` (standard library)
* `datetime` (standard library)

> Make sure to run this on a machine with a stable internet connection.

* * *

### Usage

Run the script directly to start listening for DEX logs:

```bash
python sol_dex_logs.py
```

The script will:

1. Connect to `wss://api.mainnet-beta.solana.com/`
2. Subscribe to all logs with `logsSubscribe`
3. Detect DEX-related program IDs
4. Decode and save matching logs to `dexlog.json`

### Output Format

Each line in `dexlog.json` is a JSON object with the following fields:

```json
{
  "hexsize": 214,
  "timestamp": "2025-06-14T18:33:31.563657+00:00",
  "txid": "289vyUpkBvufkDxo4JmAPhdFzzrBSYT8QY1AVc4aTHywWqD4WxSqM5sV4HF49aQoyEeepk5JEA2eCiaPfNr2rur4",
  "programid": "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",
  "dexname": "MeteoraDLMM",
  "base64": "base64encodeddata...",
  "hex": "decodedhexdata..."
}
```

### Configuration

You can customize the `programids` dictionary directly in the `__main__` block to track different programs or add/remove supported DEXes.

To change the output file:

```python
collector = SolDexLogs(programids, outputfile="customfile.json")
```

* * *

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit them (`git commit -m "Add your feature"`).
4. Push to your branch (`git push origin feature/your-feature`).
5. Open a pull request with a clear description of your changes.

Ensure your code follows PEP 8 style guidelines and includes appropriate tests.

* * *

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

* * *

## Contact

For issues, suggestions, or questions, please open an issue on GitHub or contact the maintainer at [GitHub Issues](https://github.com/neoslab/soldexlogs/issues).