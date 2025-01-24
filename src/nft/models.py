from django.db import models

class NFT(models.Model):
    transaction_hash = models.CharField(max_length=66, unique=True)
    token_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'nft'