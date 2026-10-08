# id: https://github.com/CodyCBakerPhD/md-lines-pre-commit/schema/md_lines
# description: Options for, and results of, reflowing Markdown so that each sentence sits on its own line. The Python dataclasses in md_lines/models.py are generated from this schema with `gen-python --no-metadata`; do not edit them by hand.
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Boolean, Integer, String
from linkml_runtime.utils.metamodelcore import Bool

metamodel_version = "1.11.0"
version = None

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
MD_LINES = CurieNamespace('md_lines', 'https://github.com/CodyCBakerPhD/md-lines-pre-commit/schema/md_lines/')
DEFAULT_ = MD_LINES


# Types

# Class references



@dataclass(repr=False)
class Options(YAMLRoot):
    """
    What counts as a line and a sentence.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = MD_LINES["Options"]
    class_class_curie: ClassVar[str] = "md_lines:Options"
    class_name: ClassVar[str] = "Options"
    class_model_uri: ClassVar[URIRef] = MD_LINES.Options

    split_lists: Optional[Union[bool, Bool]] = False
    keep_breaks_after: Optional[str] = ".!?"
    abbreviations: Optional[Union[str, list[str]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.split_lists is not None and not isinstance(self.split_lists, Bool):
            self.split_lists = Bool(self.split_lists)

        if self.keep_breaks_after is not None and not isinstance(self.keep_breaks_after, str):
            self.keep_breaks_after = str(self.keep_breaks_after)

        if not isinstance(self.abbreviations, list):
            self.abbreviations = [self.abbreviations] if self.abbreviations is not None else []
        self.abbreviations = [v if isinstance(v, str) else str(v) for v in self.abbreviations]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Problem(YAMLRoot):
    """
    One thing that was wrong with a file.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = MD_LINES["Problem"]
    class_class_curie: ClassVar[str] = "md_lines:Problem"
    class_name: ClassVar[str] = "Problem"
    class_model_uri: ClassVar[URIRef] = MD_LINES.Problem

    line: int = None
    message: str = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.line):
            self.MissingRequiredField("line")
        if not isinstance(self.line, int):
            self.line = int(self.line)

        if self._is_empty(self.message):
            self.MissingRequiredField("message")
        if not isinstance(self.message, str):
            self.message = str(self.message)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Result(YAMLRoot):
    """
    The reflowed text and the problems that were found.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = MD_LINES["Result"]
    class_class_curie: ClassVar[str] = "md_lines:Result"
    class_name: ClassVar[str] = "Result"
    class_model_uri: ClassVar[URIRef] = MD_LINES.Result

    text: str = None
    problems: Optional[Union[Union[dict, Problem], list[Union[dict, Problem]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.text):
            self.MissingRequiredField("text")
        if not isinstance(self.text, str):
            self.text = str(self.text)

        self._normalize_inlined_as_list(slot_name="problems", slot_type=Problem, key_name="line", keyed=False)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Paragraph(YAMLRoot):
    """
    A paragraph's position in the source, as line indices from the parser; the only block type whose lines are
    reflowed.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = MD_LINES["Paragraph"]
    class_class_curie: ClassVar[str] = "md_lines:Paragraph"
    class_name: ClassVar[str] = "Paragraph"
    class_model_uri: ClassVar[URIRef] = MD_LINES.Paragraph

    start: int = None
    end: int = None
    in_list: Union[bool, Bool] = None
    starts_item: Union[bool, Bool] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.start):
            self.MissingRequiredField("start")
        if not isinstance(self.start, int):
            self.start = int(self.start)

        if self._is_empty(self.end):
            self.MissingRequiredField("end")
        if not isinstance(self.end, int):
            self.end = int(self.end)

        if self._is_empty(self.in_list):
            self.MissingRequiredField("in_list")
        if not isinstance(self.in_list, Bool):
            self.in_list = Bool(self.in_list)

        if self._is_empty(self.starts_item):
            self.MissingRequiredField("starts_item")
        if not isinstance(self.starts_item, Bool):
            self.starts_item = Bool(self.starts_item)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.options__split_lists = Slot(uri=MD_LINES.split_lists, name="options__split_lists", curie=MD_LINES.curie('split_lists'),
                   model_uri=MD_LINES.options__split_lists, domain=None, range=Optional[Union[bool, Bool]])

slots.options__keep_breaks_after = Slot(uri=MD_LINES.keep_breaks_after, name="options__keep_breaks_after", curie=MD_LINES.curie('keep_breaks_after'),
                   model_uri=MD_LINES.options__keep_breaks_after, domain=None, range=Optional[str])

slots.options__abbreviations = Slot(uri=MD_LINES.abbreviations, name="options__abbreviations", curie=MD_LINES.curie('abbreviations'),
                   model_uri=MD_LINES.options__abbreviations, domain=None, range=Optional[Union[str, list[str]]])

slots.problem__line = Slot(uri=MD_LINES.line, name="problem__line", curie=MD_LINES.curie('line'),
                   model_uri=MD_LINES.problem__line, domain=None, range=int)

slots.problem__message = Slot(uri=MD_LINES.message, name="problem__message", curie=MD_LINES.curie('message'),
                   model_uri=MD_LINES.problem__message, domain=None, range=str)

slots.result__text = Slot(uri=MD_LINES.text, name="result__text", curie=MD_LINES.curie('text'),
                   model_uri=MD_LINES.result__text, domain=None, range=str)

slots.result__problems = Slot(uri=MD_LINES.problems, name="result__problems", curie=MD_LINES.curie('problems'),
                   model_uri=MD_LINES.result__problems, domain=None, range=Optional[Union[Union[dict, Problem], list[Union[dict, Problem]]]])

slots.paragraph__start = Slot(uri=MD_LINES.start, name="paragraph__start", curie=MD_LINES.curie('start'),
                   model_uri=MD_LINES.paragraph__start, domain=None, range=int)

slots.paragraph__end = Slot(uri=MD_LINES.end, name="paragraph__end", curie=MD_LINES.curie('end'),
                   model_uri=MD_LINES.paragraph__end, domain=None, range=int)

slots.paragraph__in_list = Slot(uri=MD_LINES.in_list, name="paragraph__in_list", curie=MD_LINES.curie('in_list'),
                   model_uri=MD_LINES.paragraph__in_list, domain=None, range=Union[bool, Bool])

slots.paragraph__starts_item = Slot(uri=MD_LINES.starts_item, name="paragraph__starts_item", curie=MD_LINES.curie('starts_item'),
                   model_uri=MD_LINES.paragraph__starts_item, domain=None, range=Union[bool, Bool])

