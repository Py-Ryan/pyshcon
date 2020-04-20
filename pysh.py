# -*- coding: UTF-8 -*-

import re
from typing import Set, Optional, Dict, List


class Char(str):
    """Represents a C++ like char data-type.

        Attributes:
            value: (str)
                Returns the character.
    """

    def __init__(self, _char: str) -> None:
        if len(_char) == 1 and _char.isprintable():
            self._char: str = _char
        else:
            raise ValueError(f'Invalid argument _char: {_char}')
            self._char = super()

    def __repr__(self) -> str:
        return repr(self._char)[1:-1]

    @property
    def value(self) -> str:
        return self._char


class Hex(str):
    """Represents a two digit hexadecimal code.

        Attributes:
            value: (str)
                The hexadecimal code.
    """

    def __init__(self, _hex: str) -> None:
        self.regex = re.compile('[aA-fF][0-9]|^[0-9][aA-fF]|^[0-9][0-9]')
        if len(_hex) == 2 and re.match(self.regex, _hex):
            self.__hex__: str = _hex
        else:
            raise ValueError(f'Invalid argument _hex: {_hex}.')
            self.__hex__ = super()

    def __repr__(self) -> str:
        return repr(self.__hex__)[1:-1]

    @property
    def value(self) -> str:
        return self.__hex__


class Pair:
    """Represents an Sh [ Char : Hex ] pair."""

    def __init__(self, _char: Char, _hex: Hex) -> None:
        try:
            self.char: Char = Char(_char).value
            self.hex: Hex = Hex(_hex).value
        except Exception as msg:
            raise Exception(msg)

    def __repr__(self) -> str:
        return repr(f'<class Pair>: [{self.char}, {self.hex}]')


class Pysh:
    """Represents an instance of Pysh."""

    def __init__(self, auto_populate: bool = True, debug: bool = False) -> None:
        self.auto_populate: bool = auto_populate
        self.debug: bool = debug
        self.__pairs__: Set[Pair] = []  # used to store Pairs
        self.__cache__: Set[Dict[str]] = []  # used to store plain_text : hex_digest pairs to prevent redundancy.

        if self.auto_populate:
            self.populate_pairs()

    def __update_cache__(self, plain_text: Optional[str] = None, hex_digest: Optional[str] = None, action: str = 'add') -> None:
        """Update Sh translation cache.

            Parameters:
                plain_text: (typing.Optional[str])
                    The plain text of the desired cache entry.
                hex_digest: (typing.Optional[str])
                    The hex digest of the desired cache entry.
                action: (str)
                    Whether to 'add' or 'delete' a cache entry.

            Return Type:
                None
        """

        cache_pair: dict = dict()
        cache_pair['plain_text'] = plain_text
        cache_pair['hex_digest'] = hex_digest

        if action == 'add' and cache_pair not in self.__cache__:
            self.__cache__.append(cache_pair)
        elif action == 'delete' and cache_pair in self.__cache__:
            self.__cache__.remove(cache_pair)

    def __retrieve_cache__(self, plain_text: Optional[str] = None, hex_digest: Optional[str] = None) -> Optional[Set[dict]]:
        """Try and retrieve a cache entry by one or both of the parameters.

            Parameters:
                plain_text: (typing.Optional[str])
                    The plain text of the desired cache entry.
                hex_digest: (typing.Optional[str])
                    The hex digest of the desired cache entry.

            Return Type:
                typing.Optional[dict]
        """

        for cache_entry in self.__cache__:
            try:
                if cache_entry['plain_text'] == plain_text or cache_entry['hex_digest'] == hex_digest:
                    return cache_entry
            except KeyError:
                pass

    def populate_pairs(self, file: str = 'data/pairs.txt', comment_symbol: str = '##') -> None:
        """Populate pairs from file.

            file: (str)
                The relative path to the file to parse.
            comment_symbol: (str)
                Ignore any lines beginning with comment_symbol

            Return Type:
                None
        """

        try:
            with open(file, 'r') as file:
                regex: re.Match = re.compile('^.[0-9][0-9]|^.[aA-fF][0-9]|^.[0-9][aA-fF]')
                for line in file:
                    if not line.startswith(comment_symbol):
                        line: str = str().join(_c for _c in line if _c.isprintable())  # avoid hidden 'lf' characters
                        if re.match(regex, line) and len(line) == 3:
                            _pair: Pair = Pair(line[0], line[1:])
                            self.__pairs__.append(_pair)
                        else:
                            raise ValueError(f'Invalid line inside of {file.name}: {line}')
        except Exception as msg:
            raise Exception(msg)

    def get_pair(self, by_character: Optional[str] = None, by_hex: Optional[str] = None) -> Optional[Pair]:
        """Find and retrieve a pair, if found, by at least one of the parameters.

            Parameters:
                by_character: (typing.Optional[str])
                    The char value of the desired pair.
                by_hex: (typing.Optional[str])
                    The hex value of the desired pair.

            Return Type:
                typing.Optional[Pair]
        """

        for _pair in self.__pairs__:
            if _pair.char == by_character or _pair.hex == by_hex:
                return _pair

    def hexadecimal(self, plain_text: str) -> str:
        """Convert plain-text into hexadecimals; Character by character.

            Parameters:
                plain_text: (str)
                    The plain text to convert into hexadecimals.

            Return Type:
                str
        """

        # cache check
        result1: Optional[Dict[str]] = self.__retrieve_cache__(plain_text=plain_text)
        if result1:
            return result1['hex_digest']

        # conversion
        hex_digest: str = str()

        for character_index in range(len(plain_text)):
            character: str = plain_text[character_index]
            if character.isspace():
                character = '.'
            result: Optional[Pair] = self.get_pair(by_character=character)
            if result:
                if character_index == 0:  # prevent first hex_code from beginning with a space
                    hex_digest += f'{result.hex} 00'
                else:
                    hex_digest += f' {result.hex} 00'
        if not result1:
            self.__update_cache__(plain_text=plain_text, hex_digest=hex_digest, action='add')

        return hex_digest

    def string(self, hex_digest: str) -> str:
        """Convert an Sh hex digest back into a string.

            Parameters:
                hex_digest: (str)
                    The digest to stringify.

            Return Type:
                str
        """

        # cache check
        result1 = self.__retrieve_cache__(hex_digest=hex_digest)
        if result1:
            return result1['plain_text']

        # conversion
        final: str = str()
        individual_hexes: List[str] = hex_digest.split()
        for _hex in individual_hexes:
            res: Optional[Pair] = self.get_pair(by_hex=_hex)
            if res:
                final += res.char

        return final

    def advanced_hexadecimal(self, plain_text: str) -> str:
        """Returns a hexadecimal data grid.

            Parameters:
                plain_text: (str)
                    The text to convert to raw hexadecimal data.
        """

        raise NotImplementedError
