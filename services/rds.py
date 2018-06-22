from .base import Service
import pandas as pd


class RDS(Service):
    service_name = 'rds'

    async def get_instances(self, rds):
        paginator = rds.get_paginator('describe_db_instances')
        db_instances = []
        async for response in paginator.paginate():
            for db_instance in response['DBInstances']:
                resp = await rds.list_tags_for_resource(
                    ResourceName=db_instance['DBInstanceArn']
                )
                db_instance['Project'] = 'none'
                for d in resp['TagList']:
                    if d['Key'] == 'Project':
                        db_instance['Project'] = d['Value']
                db_instances.append(db_instance)
        return rds.meta.region_name, db_instances

    async def show(self):
        instances = []
        try:
            async for region, db_instances in self.concurrent(self.get_instances):
                for inst in db_instances:
                    instances.append((
                        region,
                        inst['Project'],
                        inst['Engine'],
                        inst['DBInstanceClass'],
                        inst['DBInstanceIdentifier'],
                    ))
            df_db_instances = pd.DataFrame(
                instances, columns=['region', 'proj', 'engine', 'type', 'id'])
            print(df_db_instances.groupby(list(df_db_instances.columns)).size())
        finally:
            await self.close()
