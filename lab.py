import argparse
import hashlib
import json
import multiprocessing
import time
from typing import Optional

import matplotlib.pyplot as plt


class CardFinder:
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

    @staticmethod
    def generate_cards(bin_card: str, last_four: str, card_length: int, hash_value: str,
                       hash_func, process_num: int, total_processes: int) -> Optional[str]:
        """
        Generate possible card numbers for current process
        Args: bin_card: First 6 digits of card
            last_four: Last 4 digits of card
            card_length: Total card number length
            hash_value: Hash to compare against
            hash_func: Hash function to use
            process_num: Current process number
            total_processes: Total number of processes
        Returns: str: Found card number or None
        """
        try:
            middle_length = card_length - len(bin_card) - len(last_four)
            total_possibilities = 10 ** middle_length
            chunk_size = total_possibilities // total_processes
            start = process_num * chunk_size
            end = (process_num + 1) * chunk_size if process_num != total_processes - 1 else total_possibilities

            for middle in range(start, end):
                middle_str = f"{middle:0{middle_length}d}"
                card = bin_card + middle_str + last_four
                if hash_func(card.encode()).hexdigest() == hash_value:
                    return card
            return None
        except Exception as e:
            print(f"Error in generate_cards: {e}")
            return None

    @staticmethod
    def find_card(bins: [str], last_four: str, card_length: int,
                  hash_value: str, num_processes: int) -> Optional[str]:
        """
        Find card using multiprocessing
        Args: bins: List of BIN codes to search
            last_four: Last 4 digits of card
            card_length: Total card number length
            hash_value: Hash to compare against
            num_processes: Number of processes to use
        Returns: str: Found card number or None
        """
        try:
            if num_processes < 1:
                raise ValueError("Number of processes must be at least 1")

            with multiprocessing.Pool(processes=num_processes) as pool:
                for bin_card in bins:
                    args = [(bin_card, last_four, card_length, hash_value,
                             hashlib.sha3_384, i, num_processes)
                            for i in range(num_processes)]
                    results = pool.starmap(CardFinder.generate_cards, args)
                    for result in results:
                        if result is not None:
                            return result
            return None
        except Exception as e:
            print(f"Error in find_card: {e}")
            return None

    @staticmethod
    def measure_performance(bins: [str], last_four: str, card_length: int,
                            hash_value: str, plot_filename: str = "performance_plot.png") -> None:
        """Measure and plot performance for different process counts"""
        try:
            max_processes = int(multiprocessing.cpu_count() * 1.5)
            times = []

            for num_proc in range(1, max_processes + 1):
                start_time = time.time()
                result = CardFinder.find_card(bins, last_four, card_length,
                                              hash_value, num_proc)
                elapsed = time.time() - start_time
                times.append(elapsed)
                print(f"Processes: {num_proc}, Time: {elapsed} sec")

            # Plot results
            plt.plot(range(1, max_processes + 1), times, 'bo-')
            min_time = min(times)
            min_index = times.index(min_time)
            plt.plot(min_index + 1, min_time, 'ro',
                     label=f'Fastest: {min_time:} sec at {min_index + 1} processes')

            plt.xlabel('Number of processes')
            plt.ylabel('Execution time (sec)')
            plt.title('Performance by number of processes')
            plt.grid(True)
            plt.legend()

            plt.savefig(plot_filename)
            print(f"Performance plot saved as {plot_filename}")

            plt.show()
        except Exception as e:
            print(f"Error in measure_performance: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Credit Card Finder and Validator")

    # Main parameters (required for all modes)
    parser.add_argument('--bins', nargs='+', required=True,
                        help="BIN codes (first 6 digits) to search")
    parser.add_argument('--length', type=int, required=True,
                        help="Length of card numbers")
    parser.add_argument('--hash', required=True,
                        help="SHA3-384 hash of the card number to find")
    parser.add_argument('--last-four', required=True,
                        help="Last 4 digits of the card number to find")

    subparsers = parser.add_subparsers(dest='mode', required=True,
                                       help='Available modes')

    find_parser = subparsers.add_parser('find', help='Find card by hash')
    find_parser.add_argument('-p', '--processes', type=int,
                             default=multiprocessing.cpu_count(),
                             help=f'Number of processes (default: CPU count)')

    validate_parser = subparsers.add_parser('validate', help='Validate card with Luhn algorithm')
    validate_parser.add_argument('card_number', help='Card number to validate')

    perf_parser = subparsers.add_parser('performance', help='Measure performance')
    perf_parser.add_argument('--plot', default="performance_plot.png",
                             help='Filename to save performance plot')

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        if args.mode == "find":
            print(f"Searching with {args.processes} processes...")
            card = CardFinder.find_card(
                bins=args.bins,
                last_four=args.last_four,
                card_length=args.length,
                hash_value=args.hash,
                num_processes=args.processes
            )
            if card:
                with open('card.json', 'w') as f:
                    json.dump({"card_number": card}, f)
                print(f"Found card: {card}")
            else:
                print("Card not found")

        elif args.mode == "validate":
            card = args.card_number
            if CardFinder.luhn_check(card):
                print("Card is valid (Luhn check passed)")
            else:
                print("Card is invalid (Luhn check failed)")

        elif args.mode == "performance":
            CardFinder.measure_performance(
                bins=args.bins,
                last_four=args.last_four,
                card_length=args.length,
                hash_value=args.hash,
                plot_filename=args.plot
            )

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == '__main__':
    main()
