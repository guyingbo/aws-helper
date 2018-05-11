from .base import Service
import pandas as pd


class RDS(Service):
    service_name = 'rds'

    async def get_instances(self, client):
        response = await client.describe_db_instances()
        return client.meta.region_name, response['DBInstances']

    async def show(self):
        instances = []
        async for region, db_instances in self.concurrent(self.get_instances):
            for inst in db_instances:
                instances.append((
                    region,
                    inst['Engine'],
                    inst['DBInstanceClass'],
                    inst['DBInstanceIdentifier'],
                ))
        df_db_instances = pd.DataFrame(
            instances, columns=['region', 'engine', 'type', 'id'])
        print(df_db_instances.groupby(list(df_db_instances.columns)).size())
        await self.close()
