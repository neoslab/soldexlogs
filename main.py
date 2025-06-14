# === Import libraries ===
import asyncio
import base64
import json
import re
import websockets

# === Import packages ===
from datetime import datetime
from datetime import UTC
from pathlib import Path
from collections import OrderedDict


# === Class 'SolDexLogs' ===
class SolDexLogs:
    """
    This class listens to all Solana mainnet logs and detects specific DEX-related program IDs in transaction logs.
    It filters and identifies base64-encoded log data for known DEX programs, decodes them, and stores detailed entries
    into a JSON Lines formatted output file. This utility is essential for monitoring, debugging, and auditing logs
    related to specific decentralized exchange smart contracts on the Solana blockchain.

    Parameters:
    - progids (dict): A dictionary mapping known Solana program IDs (str) to their associated DEX names (str).
    - outputfile (str): The path of the file to store the matched logs. Defaults to "dexlog.json".

    Returns:
    - None
    """

    # === Function '__init__' ===
    def __init__(self, progids: dict, outputfile: str = "dexlog.json"):
        """
        This initializer sets up internal data structures and compiles a regex pattern for identifying
        log lines corresponding to Solana program invocations. It processes and stores the list of known
        DEX-related program IDs, prepares the output file path for writing, and initializes the pattern
        used for extracting program IDs from log lines. The setup is essential before the WebSocket log
        subscription begins.

        Parameters:
        - progids (dict): A mapping from Solana program IDs (str) to DEX names (str) for filtering.
        - outputfile (str): A string path to the file where logs will be appended. Defaults to "dexlog.json".

        Returns:
        - None
        """
        self.programids = {k.strip(): v for k, v in progids.items()}
        self.outputfile = Path(outputfile)
        self.logpattern = re.compile(r"Program (\w{32,}) invoke")

    # === Function 'savelog' ===
    def savelog(self, entry: OrderedDict):
        """
        This function appends a decoded and formatted log entry to the output JSON file specified
        at initialization. It opens the file in append mode, encodes the dictionary as a JSON string,
        and writes each entry on a new line for easy JSON Lines processing. This function is only
        triggered when a matching DEX log is found and successfully parsed.

        Parameters:
        - entry (OrderedDict): A dictionary-like object containing timestamped, decoded log data related to a specific DEX program activity.

        Returns:
        - None
        """
        with self.outputfile.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    # === Function 'handler' ===
    async def handler(self, message: dict):
        """
        Handles incoming WebSocket messages from the Solana logs feed. Filters non-log messages,
        extracts the transaction signature, matches program invocations, and identifies logs with
        base64-encoded payloads. For each matching log, it decodes the data, extracts hex values,
        computes the binary size, builds a structured dictionary of information, and saves the result
        using `savelog`.

        Parameters:
        - message (dict): The incoming WebSocket message dictionary containing log notifications and transaction details.

        Returns:
        - None
        """
        if message.get("method") != "logsNotification":
            return

        resp = message["params"]["result"]
        txid = resp.get("value", {}).get("signature", "")
        logs = resp.get("value", {}).get("logs", [])

        invokedids = {
            match.group(1) for log in logs
            if (match := self.logpattern.search(log))
        }

        timestamp = datetime.now(UTC).isoformat()
        for pid in invokedids:
            if pid not in self.programids:
                continue

            dexname = self.programids[pid]
            print(f"[+] Matched DEX Program: {dexname} ({pid}) in tx {txid}")

            for log in logs:
                if log.startswith("Program data:"):
                    b64data = log.split("Program data:")[-1].strip()
                    try:
                        binary_data = base64.b64decode(b64data)
                        hexdata = binary_data.hex()
                        hexsize = len(binary_data)
                    except Exception as e:
                        print(f"[-] Base64 decode failed: {e}")
                        continue

                    entry = OrderedDict()
                    entry["hexsize"] = hexsize
                    entry["timestamp"] = timestamp
                    entry["txid"] = txid
                    entry["programid"] = pid
                    entry["dexname"] = dexname
                    entry["base64"] = b64data
                    entry["hex"] = hexdata

                    print(f"[✓] Captured {dexname} log from {txid} ({hexsize} bytes)")
                    self.savelog(entry)

    # === Function 'run' ===
    async def run(self):
        """
        Connects to the Solana mainnet WebSocket endpoint and subscribes to all logs with commitment
        level 'processed'. Continuously receives log messages, decodes them, and dispatches them to
        the `handler` function. This function maintains a persistent connection and is intended to
        be run inside an asyncio event loop for real-time monitoring.

        Parameters:
        - None

        Returns:
        - None
        """
        uri = "wss://api.mainnet-beta.solana.com/"
        async with websockets.connect(uri) as ws:
            sub_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "logsSubscribe",
                "params": [
                    "all",
                    {"commitment": "processed"}
                ]
            }
            await ws.send(json.dumps(sub_msg))
            print("[*] Subscribed to ALL Solana logs.")

            while True:
                try:
                    raw = await ws.recv()
                    message = json.loads(raw)
                    await self.handler(message)
                except Exception as e:
                    print(f"[!] WebSocket error: {e}")
                    
                    
# === Main Callback ===
if __name__ == "__main__":
    """
    Main execution entry point for the SolDexLogs log monitoring tool. Initializes a dictionary mapping
    known Solana program IDs to their respective DEX project names and creates an instance of the
    `SolDexLogs` class. Launches the asynchronous log collector using `asyncio.run`. This script should
    be run from the command line and will stay active to monitor logs in real-time.

    Parameters:
    - None

    Returns:
    - None
    """
    programids = {
        "JSW99DKmxNyREQM14SQLDykeBvEUG63TeohrvmofEiw": "ApePro",
        "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "JupiterAggV4",
        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "JupiterAggV6",
        "DCA265Vj8a9CEuX1eb1LWRnDT7uK6q1xMipnNyatn23M": "JupiterDCA",
        "j1o2qRpjcyUwEvwtcfhEQefh773ZgjxcVRry7LDqg5X": "JupiterLimit",
        "6LtLpnUFNByNXLyCoK9wA2MykKAmQNZKBdY8s47dehDc": "Kamino",
        "EewxydAPCCVuNEyrVN68PuSYdQ7wKn27V9Gjeoi8dy3S": "LifinityV1",
        "2wT8Yq49kHgDzXuPxZSaeLaH1qbmGXtEyPy64bL7aD3c": "LifinityV2",
        "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo": "MeteoraDLMM",
        "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "MeteoraPools",
        "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "MeteoraDBC",
        "cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG": "MeteoraDAMM",
        "opnb2LAfJYbRMAHHvqjCwQxanZn7ReEHp1k81EohpZb": "OpenBook",
        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "OrcaWhirlpool",
        "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "OrcaSwapV1",
        "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "OrcaSwapV2",
        "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pumpfun",
        "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "Pumpswap",
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "RaydiumLP",
        "5quBtoiQqxF9Jv6KYKctB59NT3gtJD2Y65kdnB1Uev3h": "RaydiumLPAMM",
        "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "RaydiumCL",
        "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "RaydiumCPMM",
        "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "RaydiumLaunchpad",
        "stkitrT1Uoy18Dk1fTrgPw8W6MVzoCfYoAFT4MLsmhq": "SanctumRouter",
        "5ocnV1qiCgaQR8Jb8xWnVbApfaygJ8tNoZfgPwsgx9kx": "SanctumController",
        "swapNyd8XiQwJ6ianp9snpu4brUqFxadzvHebnAXjJZ": "StableWidth",
        "swapFpHZwjELNnjvThjajtiVmkz3yPQEHjLtka2fwHW": "StableWeight"
    }

    collector = SolDexLogs(programids)
    asyncio.run(collector.run())
