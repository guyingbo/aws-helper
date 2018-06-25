import asyncio
import aioboto3


class Service:
    async def get_regions(self):
        if hasattr(Service, "regions"):
            return Service.regions
        client = aioboto3.client("ec2")
        response = await client.describe_regions()
        Service.regions = [r["RegionName"] for r in response["Regions"]]
        await client.close()
        return Service.regions

    async def get_clients(self):
        if hasattr(self, "clients"):
            return self.clients
        regions = await self.get_regions()
        self.clients = [
            aioboto3.client(self.service_name, region_name=region) for region in regions
        ]
        return self.clients

    async def concurrent(self, func):
        clients = await self.get_clients()
        jobs = [func(client) for client in clients]
        for task in asyncio.as_completed(jobs):
            yield await task

    async def close(self):
        if hasattr(self, "clients"):
            for client in self.clients:
                await client.close()
