import json
import multiprocessing as mp
import time
from typing import Any, Dict

from Crypto.Hash import SHA256


class Miner():
    def __init__(self, block: Dict, difficulty: str,
                 miner_addr: str, workers: int = 4) -> None:
        """Sets parameters for the miner

        :param block: The block to be mined
        :type block: Dict
        :param difficulty: Difficulty for the block to be mined
        :type difficulty: str
        :param miner_addr: The address to be the coinbase
        :type miner_addr: str
        :param workers: [description], defaults to 4
        :type workers: int, optional
        """
        self.block = block
        self.block["coinbase"] = miner_addr
        self.difficulty = difficulty
        self.miner_addr = miner_addr
        self.workers = workers

    def hash_block(self, block_dict: Dict) -> Any:
        """Turns the dict into a string and then hashes it and checks if it is valid

        :param block_dict: Dictionary to be hashed
        :type block_dict: Dict
        :return: False if the hash isnt valid and the has and nonce in a
        tuple if it is
        :rtype: Any
        """
        json_str = json.dumps(block_dict, sort_keys=True)
        block_hash = SHA256.new(json_str.encode("UTF-8")).hexdigest()
        if block_hash[:len(self.difficulty)] == self.difficulty:
            return (block_hash, block_dict["nonce"])
        else:
            return False

    def mine_section(self, nonce_range: tuple, queue: mp.Queue) -> None:
        """Mines a batch of nonces and if any are valid submits the result
        to master process

        :param nonce_range: The range for nonces to be mined
        :type nonce_range: tuple
        :param queue: Queue to submit result to
        :type queue: mp.Queue
        """
        block_dict = self.block.copy()
        for nonce in range(nonce_range[0], nonce_range[1]):
            block_dict["nonce"] = nonce
            res = self.hash_block(block_dict)
            if res is not False:
                queue.put(res)

    def mine_block(self) -> bool:
        """Creates workers to hash batches of nonces and then wait for valid hash

        :return: True when the process has mined the block
        :rtype: bool
        """
        with mp.Pool(processes=self.workers) as pool:
            manager = mp.Manager()
            queue = manager.Queue(maxsize=1)
            nonce = 0
            batch_size = 30000
            start = time.time()
            while queue.empty():
                pool.apply_async(self.mine_section,
                                 ((nonce, nonce+batch_size), queue))
                nonce += batch_size
            res = queue.get()
            taken = time.time()-start
        self.hash = res[0]
        self.nonce = res[1]
        self.hash_speed = res[1]/taken
        return True
