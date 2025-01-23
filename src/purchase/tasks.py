from celery import shared_task
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from web3.middleware import geth_poa_middleware

from mailing_list.lib import base_email_context
from paper.models import Paper
from purchase.models import Fundraise, Purchase, Support
from researchhub.celery import QUEUE_NOTIFICATION, app
from researchhub.settings import BASE_FRONTEND_URL
from researchhub_document.models import ResearchhubPost
from user.models import User
from utils.message import send_email_message
from utils.web3_utils import web3_provider


@app.task
def update_purchases():
    PAPER_CONTENT_TYPE = ContentType.objects.get(app_label="paper", model="paper")
    purchases = Purchase.objects.filter(boost_time__gt=0)
    for purchase in purchases:
        purchase.boost_time = purchase.get_boost_time()
        purchase.save()

        if purchase.content_type == PAPER_CONTENT_TYPE:
            paper = PAPER_CONTENT_TYPE.get_object_for_this_type(id=purchase.object_id)
            paper.calculate_hot_score()


@app.task(queue=QUEUE_NOTIFICATION)
def send_support_email(
    profile_url,
    sender_name,
    recipient_name,
    email,
    amount,
    date,
    payment_type,
    email_type,
    content_type,
    object_id,
    paper_id=None,
):
    paper_data = {}
    object_supported = "profile"
    if content_type == "paper":
        paper = Paper.objects.get(id=object_id)
        url = f"{BASE_FRONTEND_URL}/paper/{paper.id}/{paper.slug}"
        paper_data["title"] = paper.title
        paper_summary = f"From Paper: {paper.summary}" if paper.summary else ""
        paper_data["summary"] = paper_summary
        paper_data["uploaded_by"] = paper.uploaded_by.full_name()
        paper_data["discussion_count"] = paper.discussion_count
        paper_data["paper_type"] = "".join(paper.paper_type.split("_")).capitalize()
        paper_data["url"] = url
        object_supported = "paper"
    elif content_type == "rhcommentmodel":
        paper = Paper.objects.get(id=paper_id)
        url = f"{BASE_FRONTEND_URL}/paper/{paper.id}/{paper.slug}#comments"
        object_supported = f"""
            <a href="{url}" class="header-link">thread</a>
        """
        object_supported = "thread"
    elif content_type == "thread":
        paper = Paper.objects.get(id=paper_id)
        url = f"{BASE_FRONTEND_URL}/paper/{paper.id}/{paper.slug}#comments"
        object_supported = f"""
            <a href="{url}" class="header-link">thread</a>
        """
        object_supported = "thread"
    elif content_type == "comment":
        paper = Paper.objects.get(id=paper_id)
        url = f"{BASE_FRONTEND_URL}/paper/{paper.id}/{paper.slug}#comments"
        object_supported = f"""
            <a href="{url}" class="header-link">comment</a>
        """
    elif content_type == "reply":
        paper = Paper.objects.get(id=paper_id)
        url = f"{BASE_FRONTEND_URL}/paper/{paper.id}/{paper.slug}#comments"
        object_supported = f"""
            <a href="{url}" class="header-link">reply</a>
        """
    elif content_type == "summary":
        paper = Paper.objects.get(id=paper_id)
        url = f"{BASE_FRONTEND_URL}/paper/{paper.id}/{paper.slug}#summary"
        object_supported = f"""
            <a href="{url}" class="header-link">summary</a>
        """
    elif content_type == "bulletpoint":
        paper = Paper.objects.get(id=paper_id)
        url = f"{BASE_FRONTEND_URL}/paper/{paper.id}/{paper.slug}#takeaways"
        object_supported = f"""
            <a href="{url}" class="header-link">key takeaway</a>
        """
    elif content_type == "researchhubpost":
        post = ResearchhubPost.objects.get(id=object_id)
        url = f"{BASE_FRONTEND_URL}/post/{post.id}/{post.slug}"
        object_supported = f"""
            <a href="{url}" class="header-link">key takeaway</a>
        """

    if payment_type == Support.PAYPAL:
        payment_type = "Paypal"
    elif payment_type == Support.ETH:
        payment_type = "Ethereum"
    elif payment_type == Support.BTC:
        payment_type = "Bitcoin"
    elif payment_type in Support.RSC_ON_CHAIN:
        payment_type = "RSC"
    elif payment_type in Support.RSC_OFF_CHAIN:
        payment_type = "RSC"

    context = {
        **base_email_context,
        "amount": amount,
        "date": date,
        "method": payment_type,
        "email": email,
        "recipient": email_type == "recipient",
        "sender_name": sender_name,
        "recipient_name": recipient_name,
        "paper": paper_data,
        "user_profile": profile_url,
        "object_supported": object_supported,
        "url": url,
    }

    if email_type == "sender":
        subject = "Receipt From ResearchHub"
        send_email_message(
            email,
            "support_receipt.txt",
            subject,
            context,
            html_template="support_receipt.html",
        )
    elif email_type == "recipient":
        subject = "Someone Sent You RSC on ResearchHub!"
        send_email_message(
            email,
            "support_receipt.txt",
            subject,
            context,
            html_template="support_receipt.html",
        )


@shared_task
def mint_fundraise_nfts(user_id, fundraise_id, contribution_amount):
    """
    Mint NFTs based on contribution amount and fundraise settings
    """
    user = User.objects.get(id=user_id)
    fundraise = Fundraise.objects.get(id=fundraise_id)

    # Check if NFT should be minted
    if not fundraise.has_nft or contribution_amount < fundraise.min_rsc_for_nft:
        return None

    w3 = web3_provider.base
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    contract_address = w3.to_checksum_address(settings.FUNDRAISE_NFT_CONTRACT_ADDRESS)
    contract = w3.eth.contract(
        address=contract_address, abi=settings.FUNDRAISE_NFT_CONTRACT_ABI
    )

    # Set metadata if not already set
    if not contract.functions.fundraiseMetadata(fundraise.id).call():
        metadata_tx = contract.functions.setFundraiseMetadata(
            fundraise.id,
            fundraise.nft_image_url or "https://default-nft-image.researchhub.com",
            fundraise.nft_name or f"ResearchHub Fundraise #{fundraise.id}",
            fundraise.nft_description or "ResearchHub Fundraise NFT",
        ).build_transaction(
            {
                "from": settings.WEB3_WALLET_ADDRESS,
                "nonce": w3.eth.get_transaction_count(settings.WEB3_WALLET_ADDRESS),
                "maxFeePerGas": w3.eth.max_priority_fee + (2 * 10**9),
                "maxPriorityFeePerGas": 2 * 10**9,
            }
        )

        signed_tx = w3.eth.account.sign_transaction(
            metadata_tx, settings.WEB3_PRIVATE_KEY
        )
        w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        w3.eth.wait_for_transaction_receipt(signed_tx.hash)

    # Mint NFT
    mint_tx = contract.functions.mint(
        user.wallet_address, fundraise.id
    ).build_transaction(
        {
            "from": settings.WEB3_WALLET_ADDRESS,
            "nonce": w3.eth.get_transaction_count(settings.WEB3_WALLET_ADDRESS),
            "maxFeePerGas": w3.eth.max_priority_fee + (2 * 10**9),
            "maxPriorityFeePerGas": 2 * 10**9,
        }
    )

    signed_tx = w3.eth.account.sign_transaction(mint_tx, settings.WEB3_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt["status"] != 1:
        raise Exception("Transaction failed")

    return receipt["transactionHash"].hex()
