from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4, UUID

from pydantic import validator, Field
from requests import Response

from pyccsi.schema import JsonCCSISchema, BaseModelSetter


class STATUS(Enum):
    READY = 1
    PENDING = 2
    FAILED = 3
    TOO_MUCH_REQUESTS = 4


class Resource(BaseModelSetter):
    link: Optional[str]
    title: Optional[Union[str, UUID]]
    response: Optional[Response] = Field(default=None)
    status: Optional[STATUS] = Field(default=STATUS.PENDING)
    index: int

    @validator('title', pre=True)
    def set_title(cls, title):
        if not title:
            return uuid4()
        return title

    class Config:
        arbitrary_types_allowed = True


class Parser:

    def __call__(self, feeds: JsonCCSISchema) -> List[Resource]:
        resources = []
        for index, entry in enumerate(feeds):
            link, title = None, None
            for tag in entry.entry:
                if tag.tag == 'link' and tag.attrib.rel == 'enclosure':
                    link = tag.attrib.href
                elif tag.tag == 'title':
                    title = tag.text
            resources.append(Resource(link=link, title=title, index=index))

        return resources