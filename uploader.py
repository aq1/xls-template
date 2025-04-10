import asyncio
import os

import httpx

from common import Error
from log import log
from settings import get_settings


async def create_dir_if_not_exists(client: httpx.AsyncClient, path: str):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    r = await client.get(url, params={"path": path})
    if r.is_success:
        return True, ""

    if r.status_code != 404:
        return False, r.text

    r = await client.put(url, params={"path": path})
    if not r.is_success:
        return False, r.text
    return True, path


async def upload_worker(client: httpx.AsyncClient, path: str, ya_disk_prefix: str):
    params = {
        "path": ya_disk_prefix + os.path.split(path)[1],
        "overwrite": "true",
    }

    response = await client.get(
        "https://cloud-api.yandex.net/v1/disk/resources/upload",
        params=params,
    )
    if not response.is_success:
        return Error(response.text)

    try:
        upload_url = response.json()["href"]
    except Exception as e:
        return Error(f"Failed to get upload_url {e}")

    with open(path, "rb") as f:
        files = {"file": f}
        response = await client.put(upload_url, files=files)
        if not response.is_success:
            return Error(response.text)

    return upload_url


async def do_upload_reports(paths: list[str]):
    settings = get_settings()
    headers = {"Authorization": f"OAuth {settings.yandex_token}"}

    async with httpx.AsyncClient(headers=headers) as client:
        ok, err = await create_dir_if_not_exists(client, settings.yandex_path)
        if ok:
            log(f"Created yandex directory {settings.yandex_path}")
        else:
            return [Error(f"Failed to create yandex directory {err}")]

        tasks = [upload_worker(client, path, settings.yandex_path) for path in paths]
        results = await asyncio.gather(*tasks)
        results = list(filter(lambda r: r is not None, results))

    return results


async def share_file_worker(client: httpx.AsyncClient, path: str, ya_disk_prefix: str):
    params = {
        "path": ya_disk_prefix + os.path.split(path)[1]
    }
    response = await client.put(
        "https://cloud-api.yandex.net/v1/disk/resources/publish",
        params=params,
    )
    try:
        response.raise_for_status()
        response = await client.get(
            "https://cloud-api.yandex.net/v1/disk/resources",
            params=params,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return Error(response.text)
    return data["public_url"]


async def do_share_files(paths: list[str]):
    settings = get_settings()
    headers = {"Authorization": f"OAuth {settings.yandex_token}"}

    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [
            share_file_worker(client, path, settings.yandex_path) for path in paths
        ]
        results = await asyncio.gather(*tasks)
        results = list(filter(lambda r: r is not None, results))

    return results


def upload_reports(filenames: list[str]):
    results = asyncio.run(do_upload_reports(filenames))
    errors = list(filter(lambda r: isinstance(r, Error), results))

    if errors:
        return False, errors

    return True, results


def share_files(filenames: list[str]):
    results = asyncio.run(do_share_files(filenames))
    errors = list(filter(lambda r: isinstance(r, Error), results))

    if errors:
        return False, errors

    return True, results
