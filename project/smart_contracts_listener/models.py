from datetime import datetime

from django.db import models
from pytz import utc


class TotalDistributionEventManager(models.Manager):
    def create_from_event_data(self, event_data):
        qs = TotalDistributionEvent.objects.filter(transaction_hash=event_data['transactionHash'].hex(),
                                                   log_index=event_data['logIndex'])
        if not qs.exists():
            event_time = datetime.utcfromtimestamp(event_data['timestamp']).replace(tzinfo=utc)
            return TotalDistributionEvent.objects.create(
                created_at=event_time,
                block_id=event_data['blockNumber'],
                transaction_hash=event_data['transactionHash'].hex(),
                log_index=event_data['logIndex'],
                input_aix_amount=event_data['args']['inputAixAmount'],
                distributed_aix_amount=event_data['args']['distributedAixAmount'],
                swapped_eth_amount=event_data['args']['swappedEthAmount'],
                distributed_eth_amount=event_data['args']['distributedEthAmount'],
            )
        return qs.first()


class TotalDistributionEvent(models.Model):
    class Meta:
        ordering = ('created_at',)
        unique_together = ('transaction_hash', 'log_index')

    created_at = models.DateTimeField()
    block_id = models.BigIntegerField()
    transaction_hash = models.TextField()
    log_index = models.PositiveSmallIntegerField()
    input_aix_amount = models.DecimalField(max_digits=40, decimal_places=0)
    distributed_aix_amount = models.DecimalField(max_digits=40, decimal_places=0)
    swapped_eth_amount = models.DecimalField(max_digits=40, decimal_places=0)
    distributed_eth_amount = models.DecimalField(max_digits=40, decimal_places=0)

    objects = TotalDistributionEventManager()
