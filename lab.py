import hashlib
import json
import multiprocessing
import time
from typing import Optional

import matplotlib.pyplot as plt

from constants import *



class CardFinder:
    def __init__(self):
        self.hash_value: str = HASH_VALUE
        self.last_four: str = LAST_FOUR
        self.bins: [str] = BINS
        self.card_length: int = CARD_LENGTH
        self.hash_func = hashlib.sha3_384

    @staticmethod
    def luhn_check(card_number: str) -> bool:
        """
        Validate card number using Luhn algorithm
        Args: card_number: Card number to validate
        Returns: bool: True if valid, False otherwise
        """
        try:
            digits = [int(d) for d in card_number]
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            total = sum(odd_digits)
            for d in even_digits:
                total += sum(divmod(d * 2, 10))
            return total % 10 == 0
        except (ValueError, IndexError):
            return False

    def generate_cards(self, bin_card: str, last_four: str,
                       process_num: int, total_processes: int) -> Optional[str]:
        """
        Generate possible card numbers for current process
        Args: bin_card: First 6 digits of card
            last_four: Last 4 digits of card
            process_num: Current process number
            total_processes: Total number of processes
        Returns: str: Found card number or None
        """
        try:
            middle_length = self.card_length - len(bin_card) - len(last_four)
            total_possibilities = 10 ** middle_length
            chunk_size = total_possibilities // total_processes
            start = process_num * chunk_size
            end = (process_num + 1) * chunk_size if process_num != total_processes - 1 else total_possibilities

            for middle in range(start, end):
                middle_str = f"{middle:0{middle_length}d}"
                card = bin_card + middle_str + last_four
                if self.hash_func(card.encode()).hexdigest() == self.hash_value:
                    return card
            return None
        except Exception as e:
            print(f"Error in generate_cards: {e}")
            return None

    def find_card(self, num_processes: int) -> Optional[str]:
        """
        Find card using multiprocessing
        Args: num_processes: Number of processes to use
        Returns: str: Found card number or None
        """
        try:
            if num_processes < 1:
                raise ValueError("Number of processes must be at least 1")

            with multiprocessing.Pool(processes=num_processes) as pool:
                for bin_card in self.bins:
                    args = [(bin_card, self.last_four, i, num_processes)
                            for i in range(num_processes)]
                    results = pool.starmap(self.generate_cards, args)
                    for result in results:
                        if result is not None:
                            return result
            return None
        except Exception as e:
            print(f"Error in find_card: {e}")
            return None

    def measure_performance(self) -> None:
        """Measure and plot performance for different process counts"""
        try:
            max_processes = int(multiprocessing.cpu_count() * 1.5)
            times = []

            for num_proc in range(1, max_processes + 1):
                start_time = time.time()
                result = self.find_card(num_proc)
                elapsed = time.time() - start_time
                times.append(elapsed)
                print(f"Processes: {num_proc}, Time: {elapsed} sec")

            # Plot results
            plt.plot(range(1, max_processes + 1), times, 'bo-')
            min_time = min(times)
            min_index = times.index(min_time)
            plt.plot(min_index + 1, min_time, 'ro')
            plt.xlabel('Number of processes')
            plt.ylabel('Execution time (sec)')
            plt.title('Performance by number of processes')
            plt.grid(True)
            plt.show()
        except Exception as e:
            print(f"Error in measure_performance: {e}")

    def run(self) -> None:
        """Main application interface"""
        print("1. Find card by hash")
        print("2. Validate card with Luhn algorithm")
        print("3. Measure performance")

        try:
            choice = input("Select mode (1-3): ")

            if choice == "1":
                num_proc = int(input(f"Enter number of processes (up to {multiprocessing.cpu_count()}): "))
                card = self.find_card(num_proc)
                if card:
                    with open('card.json', 'w') as f:
                        json.dump({"card_number": card}, f)
                    print(f"Found card: {card}")
                else:
                    print("Card not found")

            elif choice == "2":
                card = input("Enter card number to validate: ")
                if self.luhn_check(card):
                    print("Card is valid (Luhn check passed)")
                else:
                    print("Card is invalid (Luhn check failed)")

            elif choice == "3":
                self.measure_performance()
            else:
                print("Invalid choice")

        except ValueError:
            print("Invalid input format")
        except Exception as e:
            print(f"Error occurred: {e}")


if __name__ == '__main__':
    finder = CardFinder()
    finder.run()
