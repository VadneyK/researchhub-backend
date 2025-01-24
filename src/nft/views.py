from rest_framework.decorators import api_view
from rest_framework.response import Response
from web3 import Web3

from .models import NFT


@api_view(["POST"])
def verify_and_create_nft(request):
    transaction_hash = request.data.get("transactionHash")
    if not transaction_hash:
        return Response({"error": "Transaction hash required"}, status=400)

    # Initialize Web3
    w3 = Web3(
        Web3.HTTPProvider(
            "https://base-sepolia.infura.io/v3/46039066f07a492f97b4a7e7602d752c"
        )
    )

    try:
        # Get transaction receipt
        receipt = w3.eth.get_transaction_receipt(transaction_hash)

        if not receipt or not receipt["status"]:
            return Response({"error": "Invalid transaction"}, status=400)

        # Extract token ID from event logs (simplified)
        token_id = 1  # In real implementation, parse from event logs

        # Create NFT record
        nft = NFT.objects.create(
            transaction_hash=transaction_hash, token_id=token_id, verified=True
        )

        return Response({"success": True, "nft_id": nft.id, "token_id": nft.token_id})

    except Exception as e:
        return Response({"error": str(e)}, status=400)
