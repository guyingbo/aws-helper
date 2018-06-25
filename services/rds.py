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

    async def show(self, columns):
        assert len(columns) > 0
        valid_columns = set(['region', 'proj', 'engine', 'type', 'id'])
        columns = list(filter(lambda c: c in valid_columns, columns))
        instances = []
        try:
            async for region, db_instances in self.concurrent(self.get_instances):
                for inst in db_instances:
                    d = {
                        'region': region,
                        'proj': inst['Project'],
                        'engine': inst['Engine'],
                        'type': inst['DBInstanceClass'],
                        'id': inst['DBInstanceIdentifier'],
                    }
                    tup = tuple([d[column] for column in columns])
                    instances.append(tup)
            df_db_instances = pd.DataFrame(
                instances, columns=columns)
            print(df_db_instances.groupby(list(df_db_instances.columns)).size())
        finally:
            await self.close()
