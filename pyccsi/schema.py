# base classes
from typing import Optional, List, Literal

from pydantic import BaseModel, Field, PrivateAttr, validator


class BaseModelSetter(BaseModel):

    class Config:
        allow_mutation = True


class BaseModelPartialEQ(BaseModel):

    def __eq__(self, other: BaseModel):
        return all([sv == other.__dict__[sk] for sk, sv in self.__dict__.items() if sv is not None])


# schema
class Attrib(BaseModelSetter, BaseModelPartialEQ):
    href: Optional[str]
    rel: Optional[str]
    type: Optional[str]


class Tag(BaseModelSetter, BaseModelPartialEQ):
    tag: str
    text: Optional[str]
    attrib: Optional[Attrib]


class Entry(BaseModelSetter, BaseModelPartialEQ):
    entry: List[Tag] = Field(default_factory=list)


class Feed(BaseModelSetter):
    entries: List[Entry] = Field(default_factory=list)
    head: Optional[List[Tag]] = Field(default_factory=list)
    totalResults: int = Field(default=0)


# schema
class JsonCCSISchema(BaseModelSetter):
    feed: Optional[Feed]
    _level: Literal['entries', 'tags'] = PrivateAttr(default='entries')

    def __iter__(self):
        """iter trought certain level """
        for entry in self.feed.entries:
            if self._level == 'entries':
                yield entry
            for tag in entry.entry:
                if self._level == 'tags':
                    yield tag

    @validator('feed', pre=True)
    def unpack_feed(cls, value):
        if isinstance(value, list):
            return value[0]
        elif isinstance(value, Feed):
            return value

    def __next__(self):
        return self

    def __call__(self, level: Literal['feeds', 'entries', 'tags'] = 'tags'):
        self._level = level
        return self