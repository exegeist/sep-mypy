"""Helpers for interacting with type var tuples."""

from __future__ import annotations

from typing import Sequence

from mypy.types import (
    Instance,
    ProperType,
    Type,
    UnpackType,
    find_unpack_in_list,
    get_proper_type,
    split_with_prefix_and_suffix,
)


def split_with_instance(
    typ: Instance,
) -> tuple[tuple[Type, ...], tuple[Type, ...], tuple[Type, ...]]:
    assert typ.type.type_var_tuple_prefix is not None
    assert typ.type.type_var_tuple_suffix is not None
    return split_with_prefix_and_suffix(
        typ.args, typ.type.type_var_tuple_prefix, typ.type.type_var_tuple_suffix
    )


def split_with_mapped_and_template(
    mapped: tuple[Type, ...],
    mapped_prefix_len: int | None,
    mapped_suffix_len: int | None,
    template: tuple[Type, ...],
    template_prefix_len: int,
    template_suffix_len: int,
) -> (
    tuple[
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
    ]
    | None
):
    split_result = fully_split_with_mapped_and_template(
        mapped,
        mapped_prefix_len,
        mapped_suffix_len,
        template,
        template_prefix_len,
        template_suffix_len,
    )
    if split_result is None:
        return None

    (
        mapped_prefix,
        mapped_middle_prefix,
        mapped_middle_middle,
        mapped_middle_suffix,
        mapped_suffix,
        template_prefix,
        template_middle_prefix,
        template_middle_middle,
        template_middle_suffix,
        template_suffix,
    ) = split_result

    return (
        mapped_prefix + mapped_middle_prefix,
        mapped_middle_middle,
        mapped_middle_suffix + mapped_suffix,
        template_prefix + template_middle_prefix,
        template_middle_middle,
        template_middle_suffix + template_suffix,
    )


def fully_split_with_mapped_and_template(
    mapped: tuple[Type, ...],
    mapped_prefix_len: int | None,
    mapped_suffix_len: int | None,
    template: tuple[Type, ...],
    template_prefix_len: int,
    template_suffix_len: int,
) -> (
    tuple[
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
        tuple[Type, ...],
    ]
    | None
):
    if mapped_prefix_len is not None:
        assert mapped_suffix_len is not None
        mapped_prefix, mapped_middle, mapped_suffix = split_with_prefix_and_suffix(
            tuple(mapped), mapped_prefix_len, mapped_suffix_len
        )
    else:
        mapped_prefix = tuple()
        mapped_suffix = tuple()
        mapped_middle = mapped

    template_prefix, template_middle, template_suffix = split_with_prefix_and_suffix(
        tuple(template), template_prefix_len, template_suffix_len
    )

    unpack_prefix = find_unpack_in_list(template_middle)
    if unpack_prefix is None:
        return (
            mapped_prefix,
            (),
            mapped_middle,
            (),
            mapped_suffix,
            template_prefix,
            (),
            template_middle,
            (),
            template_suffix,
        )

    unpack_suffix = len(template_middle) - unpack_prefix - 1
    # mapped_middle is too short to do the unpack
    if unpack_prefix + unpack_suffix > len(mapped_middle):
        return None

    (
        mapped_middle_prefix,
        mapped_middle_middle,
        mapped_middle_suffix,
    ) = split_with_prefix_and_suffix(mapped_middle, unpack_prefix, unpack_suffix)
    (
        template_middle_prefix,
        template_middle_middle,
        template_middle_suffix,
    ) = split_with_prefix_and_suffix(template_middle, unpack_prefix, unpack_suffix)

    return (
        mapped_prefix,
        mapped_middle_prefix,
        mapped_middle_middle,
        mapped_middle_suffix,
        mapped_suffix,
        template_prefix,
        template_middle_prefix,
        template_middle_middle,
        template_middle_suffix,
        template_suffix,
    )


def extract_unpack(types: Sequence[Type]) -> ProperType | None:
    """Given a list of types, extracts either a single type from an unpack, or returns None."""
    if len(types) == 1:
        if isinstance(types[0], UnpackType):
            return get_proper_type(types[0].type)
    return None
