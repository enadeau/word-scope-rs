import logging
import sys
import time

from comb_spec_searcher import CombinatorialSpecificationSearcher
from logzero import logger

from example_py import AvoidingWithPrefix as AvoidingWithPrefix_py
from example_py import pack as pack_py
from example_rs import AvoidingWithPrefix as AvoidingWithPrefix_rs
from example_rs import pack as pack_rs

logger.setLevel(logging.WARNING)

language = sys.argv[1]
if language == "rs":
    AvoidingWithPrefix = AvoidingWithPrefix_rs
    pack = pack_rs
elif language == "py":
    AvoidingWithPrefix = AvoidingWithPrefix_py
    AvoidingWithPrefix_py.count_objects_of_size = lambda self, n: sum(
        1 for _ in self.objects_of_size(n)
    )
    pack = pack_py
else:
    raise ValueError(f"Invalid language '{language}'")

prefix = ""
patterns = ["ababa", "babb"]
alphabet = ["a", "b"]
start_class = AvoidingWithPrefix(prefix, patterns, alphabet)


searcher = CombinatorialSpecificationSearcher(start_class, pack)
start_time = time.perf_counter()
spec = searcher.auto_search()
search_time = time.perf_counter() - start_time

count_time = 0.0
brute_force_time = 0.0
for n in range(20):
    # Count
    start_time = time.perf_counter()
    count = spec.count_objects_of_size(n)
    count_time += time.perf_counter() - start_time
    # Brute force
    start_time = time.perf_counter()
    brute_force = start_class.count_objects_of_size(n)
    brute_force_time = time.perf_counter() - start_time
    # Print and assert
    # print(n, count, brute_force)
    assert count == brute_force

print(f"Search time: {search_time}")
print(f"Count time: {count_time}")
print(f"brute force time: {brute_force_time}")
