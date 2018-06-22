from .base import Service
import pandas as pd


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
            Filters=[{
                'Name': 'state',
                'Values': ['active']
            }]
        )
        for inst in response['ReservedInstances']:
            result.append((
                ec2.meta.region_name,
                inst['InstanceType'],
                inst['InstanceCount']
            ))
        return result

    async def get_ec2_instances(self, ec2):
        instances = []
        paginator = ec2.get_paginator('describe_instances')
        async for response in paginator.paginate(
            Filters=[{
                'Name': 'instance-state-name',
                'Values': ['running', 'stopped']
            }]
        ):
            reservations = response['Reservations']
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
        try:
            index = list(df_stats.columns).index('on-demand')
        except ValueError:
            df_stats.loc[:, 'reserved'] = 0
        else:
            df_stats.insert(index+1, 'reserved', 0)
        async for result in self.concurrent(self.get_reserved_instances):
            for region, typ, count in result:
                df_stats.loc[(region, typ), 'reserved'] += count
        print(df_stats.to_string())
        await self.close()
