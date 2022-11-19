from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep as timesleep
from requests import get, Response
from pydantic import BaseModel, Field,  validator, HttpUrl
from typing import Optional, List, Union, Type
from pathlib import Path
from termcolor import colored

from pyccsi.parser import Parser, Resource, STATUS
from pyccsi.schema import JsonCCSISchema, Tag, Attrib

# helper func
def create_fld_if_not_exist(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

# constants
# BASE_URL = "http://185.226.13.104"
BASE_URL = "http://localhost:5000"


class CCSIRequester(BaseModel):
    host_url: HttpUrl
    resource: str
    params: Optional[Union[dict, BaseModel]]
    schemas: Type[JsonCCSISchema]
    parser: Parser
    records: List[Resource] = Field(default_factory=list)

    @validator('params', pre=True)
    def set_params(cls, value):
        if isinstance(value, BaseModel):
            return value.dict(by_alias=True)
        elif isinstance(value, dict):
            return value

    @validator('host_url', pre=True)
    def check_host_url(cls, value: str):
        if value.endswith('/'):
            raise ValueError('Base url has to end without "/" character')
        else:
            return value

    def run(self) -> List[Resource]:
        response = self.send_request()
        feed = self.parse_response(response)
        self.parse_feed(feed)
        self.get_next(feed)
        return self.records

    def parse_feed(self, feed: JsonCCSISchema):
        self.records += self.parser(feed)

    def parse_response(self, response: Response)-> JsonCCSISchema:
        return self.schemas(feed=response.json())

    def get_next(self, feed: JsonCCSISchema)-> None:
        for tag in feed.feed.head:
            if Tag(tag='link', attrib=Attrib(rel='next')) == tag:
                next = tag
        # if any(next:=tag for tag in feed.feed.head if Tag(tag='link', attrib=Attrib(rel='next')) == tag):
        if len(self.records) == feed.feed.totalResults:
            return None
        response = get(url=next.attrib.href)
        feed = self.parse_response(response)
        self.parse_feed(feed)
        self.get_next(feed)

    def send_request(self):
        response = get(url=f"{self.base_url}/{self.resource}/json/search?", params=self.params)
        print(response.url)
        if response.status_code != 200:
            raise Exception(f"ccsi request {response.url} failed")
        return response

    class Config:
        arbitrary_types_allowed = True


def request_resource(resource: Resource) -> Resource:
    print(f' {resource.index} requested from {resource.link}')
    resource.response = get(resource.link, allow_redirects=True, stream=True)
    return resource


def resolve_status(resource: Resource) -> Resource:

    if resource.response.status_code == 200:
        print(colored(f' {resource.index} requested from {resource.link} : data ready', 'green'))
        resource.status = STATUS.READY
    elif resource.response.status_code == 201:
        print(colored(f' {resource.index} requested from {resource.link} : data pending', 'blue'))
        resource.status = STATUS.PENDING
    elif resource.response.status_code == 429:
        print(colored(f'{resource.index} requested from {resource.link} : data too much requests', 'red'))
        resource.status = STATUS.TOO_MUCH_REQUESTS
    else:
        resource.status = STATUS.FAILED
        print(colored(f' {resource.index} requested from {resource.link} : failed', 'red'))

    return resource


def download(path: Path, resource: Resource):
    print(colored(f' {resource.index} requested from {resource.title} : data download start', 'green'))
    with open(path / resource.title, 'wb') as fd:
        fd.write(resource.response.content)
        # for count, chunk in enumerate(resource.response.iter_content()):
        #     fd.write(chunk)
        #     print(colored(f' {resource.index} requested from {resource.title} : data download {count} cnunk', 'green'))
    print(colored(f' {resource.index} requested from {resource.title} : data download end', 'green'))


class Downloader(BaseModel):
    pool: List[Resource]
    path: Path
    sleep: int = Field(default=200)
    sleep_step: int = Field(default=5)
    timeout: int = Field(default=12*60)
    max_worker: int = Field(default=20)

    def run(self):
        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(self.request_data, self.pool)

    def sequential_run(self):
        for resource in self.pool:
            self.request_data(resource)

    def request_data(self, resource: Resource) ->None:
        time = 0
        while resource.status in [STATUS.PENDING, STATUS.TOO_MUCH_REQUESTS] or time <= self.timeout:
            request_resource(resource)
            resolve_status(resource)

            if resource.status == STATUS.READY:
                download(self.path, resource)
                break
            elif resource.status == STATUS.TOO_MUCH_REQUESTS or resource.status == STATUS.PENDING:
                timesleep(self.sleep)
                print(f' {resource.index} requested from {resource.link} : sleep for {self.sleep} s')
                time += self.sleep
            elif resource.status == STATUS.FAILED:
                break

    class Config:
        arbitrary_types_allowed = True

