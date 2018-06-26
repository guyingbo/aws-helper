import aioboto3
from .base import Service
from datetime import datetime, timedelta


class CloudWatch(Service):
    service_name = "cloudwatch"

    async def show(self):
        client = aioboto3.client("cloudwatch", region_name="us-east-1")
        resp = await client.get_metric_statistics(
            Namespace="AWS/ElastiCache",
            MetricName="FreeableMemory",
            Dimensions=[{"Name": "CacheClusterId", "Value": "redis-cluster"}],
            StartTime=datetime.utcnow() - timedelta(seconds=300),
            EndTime=datetime.utcnow() + timedelta(seconds=120),
            Period=60,
            Statistics=["Average"],
            Unit="Bytes",
        )
        print(resp)
        # for datapoint in resp['Datapoints']:
        #     print(datapoint)
        await client.close()
