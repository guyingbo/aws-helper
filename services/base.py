import aioboto3


class Service:
    async def get_regions(self):
        if hasattr(Service, "regions"):
            return Service.regions
        async with aioboto3.client("ec2") as client:
            response = await client.describe_regions()
            Service.regions = [r["RegionName"] for r in response["Regions"]]
        return Service.regions

    async def concurrent(self, func):
        regions = await self.get_regions()
        for region in regions:
            async with aioboto3.client(self.service_name, region_name=region) as client:
                r = await func(client)
                yield r

    async def close(self):
        if hasattr(self, "clients"):
            for client in self.clients:
                await client.close()
