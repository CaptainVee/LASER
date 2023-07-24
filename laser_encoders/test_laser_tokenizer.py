#!/usr/bin/python3
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
# LASER  Language-Agnostic SEntence Representations
# is a toolkit to calculate multilingual sentence embeddings
# and to use them for document classification, bitext filtering
# and mining
#
# --------------------------------------------------------
# Tests for LaserTokenizer

import os
import urllib.request
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from laser_encoders.laser_tokenizer import LaserTokenizer


@pytest.fixture
def tokenizer():
    with NamedTemporaryFile() as f:
        with urllib.request.urlopen(
            "https://dl.fbaipublicfiles.com/nllb/laser/laser2.spm"
        ) as response:
            f.write(response.read())
        return LaserTokenizer(spm_model=Path(f.name))


@pytest.fixture
def input_text() -> str:
    return "This is a test sentence."


def test_tokenize(tokenizer, input_text: str):
    expected_output = "▁this ▁is ▁a ▁test ▁sent ence ."
    assert tokenizer.tokenize(input_text) == expected_output


def test_normalization(tokenizer):
    test_data = "Hello!!! How are you??? I'm doing great."
    expected_output = "▁hel lo !!! ▁how ▁are ▁you ??? ▁i ' m ▁do ing ▁great ."
    assert tokenizer.tokenize(test_data) == expected_output


def test_descape(tokenizer):
    test_data = "I &lt;3 Apple &amp; Carrots!"
    expected_output = "▁i ▁<3 ▁app le ▁& ▁car ro ts !"
    tokenizer.descape = True
    assert tokenizer.tokenize(test_data) == expected_output


def test_lowercase(tokenizer):
    test_data = "THIS OUTPUT MUST BE UPPERCASE"
    expected_output = "▁TH IS ▁ OU TP UT ▁ MU ST ▁BE ▁ UP PER CA SE"
    tokenizer.lower_case = False
    assert tokenizer.tokenize(test_data) == expected_output


def test_is_printable(tokenizer):
    test_data = "Hello, \tWorld! ABC\x1f123"
    expected_output = "▁hel lo , ▁world ! ▁ab c 12 3"
    assert tokenizer.tokenize(test_data) == expected_output


def test_tokenize_file(tokenizer, input_text: str):
    with TemporaryDirectory() as temp_dir:
        input_file = os.path.join(temp_dir, "input.txt")
        output_file = os.path.join(temp_dir, "output.txt")

        with open(input_file, "w") as file:
            file.write(input_text)

        tokenizer.tokenize_file(
            inp_fname=Path(input_file),
            out_fname=Path(output_file),
        )

        with open(output_file, "r") as file:
            output = file.read().strip()

        expected_output = "▁this ▁is ▁a ▁test ▁sent ence ."
        assert output == expected_output


def test_tokenize_file_overwrite(tokenizer, input_text: str):
    with TemporaryDirectory() as temp_dir:
        input_file = os.path.join(temp_dir, "input.txt")
        output_file = os.path.join(temp_dir, "output.txt")

        with open(input_file, "w") as file:
            file.write(input_text)

        with open(output_file, "w") as file:
            file.write("Existing output")

        # Test when over_write is False
        tokenizer.over_write = False
        tokenizer.tokenize_file(
            inp_fname=Path(input_file),
            out_fname=Path(output_file),
        )

        with open(output_file, "r") as file:
            output = file.read().strip()

        assert output == "Existing output"

        # Test when over_write is True
        tokenizer.over_write = True
        tokenizer.tokenize_file(
            inp_fname=Path(input_file),
            out_fname=Path(output_file),
        )

        with open(output_file, "r") as file:
            output = file.read().strip()

        expected_output = "▁this ▁is ▁a ▁test ▁sent ence ."
        assert output == expected_output
