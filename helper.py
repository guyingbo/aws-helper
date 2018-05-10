import aioboto3
import asyncio
import pandas as pd
from datetime import datetime, timedelta
loop = asyncio.get_event_loop()


class Service:
    async def get_regions(self):
        if hasattr(Service, 'regions'):
            return Service.regions
        client = aioboto3.client('ec2')
        response = await client.describe_regions()
        Service.regions = [r['RegionName'] for r in response['Regions']]
        await client.close()
        return Service.regions

    async def get_clients(self):
        if hasattr(self, 'clients'):
            return self.clients
        regions = await self.get_regions()
        self.clients = [
            aioboto3.client(self.service_name, region_name=region)
            for region in regions
        ]
        return self.clients

    async def concurrent(self, func):
        clients = await self.get_clients()
        jobs = [func(client) for client in clients]
        for task in asyncio.as_completed(jobs):
            yield await task

    async def close(self):
        if hasattr(self, 'clients'):
            for client in self.clients:
                await client.close()

    async def __aexit__(self, exc):
        await self.close()


def get_tags(inst):
    return {dic['Key']: dic['Value'] for dic in inst.get('Tags', {})}


def get_tag(inst, key):
    tags = get_tags(inst)
    return tags.get(key, '')


def get_region(inst):
    return inst['Placement']['AvailabilityZone'][:-1]


def is_emr(inst):
    return any('aws:elasticmapreduce' in key for key in get_tags(inst))


def get_lifecycle(inst):
    emr = 'emr-' if is_emr(inst) else ''
    return emr + inst.get('InstanceLifecycle', 'on-demand')


class EC2(Service):
    service_name = 'ec2'

    async def get_reserved_instances(self, ec2):
        result = []
        response = await ec2.describe_reserved_instances(
            Filters=[{'Name': 'state', 'Values': ['active']}])
        for inst in response['ReservedInstances']:
            result.append((
                ec2.meta.region_name,
                inst['InstanceType'],
                inst['InstanceCount']
            ))
        return result

    async def get_ec2_instances(self, ec2):
        response = await ec2.describe_instances(Filters=[
            {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
        ])
        reservations = response['Reservations']
        instances = []
        for res in reservations:
            instances.extend(res['Instances'])
        return instances

    async def show(self):
        instances = []
        async for insts in self.concurrent(self.get_ec2_instances):
            instances.extend(insts)
        instances = [(
            get_region(inst),
            inst['InstanceType'],
            # inst.get('InstanceLifecycle', 'on-demand'),
            get_lifecycle(inst),
            get_tag(inst, 'Name'),
            ) for inst in instances
        ]
        df_instances = pd.DataFrame(
            instances, columns=['region', 'type', 'lifecycle', 'name'])
        # grouped = df_instances.groupby(['region', 'type']).size()
        grouped = df_instances.groupby(
            ['region', 'type', 'lifecycle'], as_index=False).count()
        df_stats = grouped.pivot_table(
            index=['region', 'type'],
            columns='lifecycle',
            values='name',
            aggfunc='sum',
            fill_value=0
        )
        # df_stats = pd.DataFrame(grouped, columns=['onDemand'])
        df_stats.loc[:, 'reserved'] = 0
        async for result in self.concurrent(self.get_reserved_instances):
            for region, typ, count in result:
                df_stats.loc[(region, typ), 'reserved'] += count
        print(df_stats.to_string())
        await self.close()


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


class CloudWatch(Service):
    service_name = 'cloudwatch'

    async def show(self):
        client = aioboto3.client('cloudwatch', region_name='us-east-1')
        resp = await client.get_metric_statistics(
            Namespace='AWS/ElastiCache',
            MetricName='FreeableMemory',
            Dimensions=[
                {
                    'Name': 'CacheClusterId',
                    'Value': 'rta-mq',
                },
                # {
                #     'Name': 'CacheNodeId',
                #     'Value': '0001',
                # }
            ],
            StartTime=datetime.utcnow() - timedelta(seconds=300),
            EndTime=datetime.utcnow() + timedelta(seconds=120),
            Period=60,
            Statistics=['Average'],
            Unit='Bytes',
        )
        print(resp)
        # for datapoint in resp['Datapoints']:
        #     print(datapoint)
        await client.close()


if __name__ == '__main__':
    rds = RDS()
    ec2 = EC2()
    # cloudwatch = CloudWatch()
    loop.run_until_complete(ec2.show())
    # loop.run_until_complete(rds.show())
    # loop.run_until_complete(cloudwatch.show())
    loop.close()
