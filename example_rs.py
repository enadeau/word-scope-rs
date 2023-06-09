"""
In this file an example of how to perform combinatorial exploration on words
with respect to factor order is given.

>>> alphabet = ['a', 'b']
>>> start_class = AvoidingWithPrefix('', ['b'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search(status_update=10)
>>> [specification.count_objects_of_size(n=i) for i in range(10)]
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

>>> start_class = AvoidingWithPrefix('', ['ab'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search(status_update=10)
>>> [specification.count_objects_of_size(n=i) for i in range(10)]
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

>>> start_class = AvoidingWithPrefix('', ['aa', 'bb'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search(status_update=10)
>>> [specification.count_objects_of_size(n=i) for i in range(10)]
[1, 2, 2, 2, 2, 2, 2, 2, 2, 2]

>>> start_class = AvoidingWithPrefix('', ['bb'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search(status_update=10)
>>> [specification.count_objects_of_size(n=i) for i in range(11)]
[1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

>>> start_class = AvoidingWithPrefix('', ['ababa', 'babb'], alphabet)
>>> searcher = CombinatorialSpecificationSearcher(start_class, pack)
>>> specification = searcher.auto_search()
>>> [specification.count_objects_of_size(n=i) for i in range(11)]
[1, 2, 4, 8, 15, 27, 48, 87, 157, 283, 511]
>>> specification.count_objects_of_size(n=15)
9798
"""
from itertools import product
from typing import Iterable, Iterator, Optional, Tuple, Union

from comb_spec_searcher import (AtomStrategy, CartesianProductStrategy,
                                CombinatorialClass, CombinatorialObject,
                                CombinatorialSpecificationSearcher,
                                DisjointUnionStrategy, StrategyPack)
from comb_spec_searcher.bijection import ParallelSpecFinder
from comb_spec_searcher.isomorphism import Bijection
from word_scope_rs import AvoidingWithPrefix, Word  # type: ignore

AvoidingWithPrefix.extra_parameters = tuple()

# the strategies

class ExpansionStrategy(DisjointUnionStrategy[AvoidingWithPrefix, Word]):
    def decomposition_function(
        self, avoiding_with_prefix: AvoidingWithPrefix
    ) -> Optional[Tuple[AvoidingWithPrefix, ...]]:
        if not avoiding_with_prefix.just_prefix:
            return tuple(avoiding_with_prefix.expand_one_letter())
        return None

    def formal_step(self) -> str:
        return "Either just the prefix, or append a letter from the alphabet"

    def forward_map(
        self,
        avoiding_with_prefix: AvoidingWithPrefix,
        word: CombinatorialObject,
        children: Optional[Tuple[AvoidingWithPrefix, ...]] = None,
    ) -> Tuple[Optional[Word], ...]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        assert isinstance(word, Word)
        if children is None:
            children = self.decomposition_function(avoiding_with_prefix)
            assert children is not None
        if len(word) == len(avoiding_with_prefix.prefix):
            return (word,) + tuple(None for i in range(len(children) - 1))
        for idx, child in enumerate(children[1:]):
            if word[: len(child.prefix)] == child.prefix:
                break
        return (
            tuple(None for _ in range(idx + 1))
            + (word,)
            + tuple(None for _ in range(len(children) - idx - 1))
        )

    def __str__(self) -> str:
        return self.formal_step()

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    @classmethod
    def from_dict(cls, d) -> "ExpansionStrategy":
        return cls()


class RemoveFrontOfPrefix(CartesianProductStrategy[AvoidingWithPrefix, Word]):
    def decomposition_function(
        self, avoiding_with_prefix: AvoidingWithPrefix
    ) -> Union[Tuple[AvoidingWithPrefix, ...], None]:
        """If the k is the maximum length of a pattern to be avoided, then any
        occurrence using indices further to the right of the prefix can use at
        most the last k - 1 letters in the prefix."""
        children = avoiding_with_prefix.remove_front_of_prefix()
        if children is not None:
            children = tuple(children)
        return children

    def formal_step(self) -> str:
        return "removing redundant prefix"

    def backward_map(
        self,
        avoiding_with_prefix: AvoidingWithPrefix,
        words: Tuple[Optional[CombinatorialObject], ...],
        children: Optional[Tuple[AvoidingWithPrefix, ...]] = None,
    ) -> Iterator[Word]:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        assert len(words) == 2
        assert isinstance(words[0], Word)
        assert isinstance(words[1], Word)
        if children is None:
            children = self.decomposition_function(avoiding_with_prefix)
            assert children is not None
        yield Word(words[0] + words[1])

    def forward_map(
        self,
        comb_class: AvoidingWithPrefix,
        word: CombinatorialObject,
        children: Optional[Tuple[AvoidingWithPrefix, ...]] = None,
    ) -> Tuple[Word, ...]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        assert isinstance(word, Word)
        if children is None:
            children = self.decomposition_function(comb_class)
            assert children is not None
        return Word(children[0].prefix), Word(word[len(children[0].prefix) :])

    @classmethod
    def from_dict(cls, d):
        return cls()

    def __str__(self) -> str:
        return self.formal_step()

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"


pack = StrategyPack(
    initial_strats=[RemoveFrontOfPrefix()],
    inferral_strats=[],
    expansion_strats=[[ExpansionStrategy()]],
    ver_strats=[AtomStrategy()],
    name=("Finding specification for words avoiding consecutive patterns."),
)


if __name__ == "__main__":
    example_alphabet = ["a", "b"]
    # input(
    #     ("Input the alphabet (letters should be separated by a" " comma):")
    # ).split(",")
    example_patterns = ("aa",)
    # tuple(
    #     map(
    #         Word,
    #         input(
    #             (
    #                 "Input the patterns to be avoided (patterns should be "
    #                 "separated by a comma):"
    #             )
    #         ).split(","),
    #     )
    # )

    start_class = AvoidingWithPrefix("", example_patterns, example_alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack, debug=False)
    spec = searcher.auto_search(status_update=10)
    print(spec)
    # print(spec.get_genf())
    import time

    for n in range(20):
        print(
            n,
            spec.count_objects_of_size(n),
            sum(1 for _ in start_class.objects_of_size(n)),
        )
