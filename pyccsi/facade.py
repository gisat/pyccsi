from pathlib import Path
from typing import Union, List

from pydantic import BaseModel

from pyccsi.downloader import CCSIRequester, Downloader
from pyccsi.parser import Resource


class CCSIDownloader:

    def __init__(self, host_url: str):
        self.host_url: str = host_url
        self.requester = None
        self.downloader = None

    def send_request(self, resource: str, params: Union[dict, BaseModel]) -> List[Resource]:
        self.requester = CCSIRequester(resource=resource, params=params, host_url=self.host_url)
        self.requester.run()
        print(f'Found {len(self.requester.records)}')
        return self.requester.records

    def download(self, path: Union[str, Path]) -> None:
        self.downloader = Downloader(pool=self.requester.records, path=path, sleep=8*60, timeout=12*60, max_worker=1)
        self.downloader.run()
