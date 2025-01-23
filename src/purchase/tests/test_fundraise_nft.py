from django.test import override_settings
from rest_framework.test import APITestCase
from web3 import Web3

from purchase.models import Fundraise
from purchase.tasks import mint_fundraise_nfts
from user.tests.helpers import create_random_authenticated_user
from utils.web3_utils import web3_provider

TEST_SETTINGS = {
    "FUNDRAISE_NFT_CONTRACT_ADDRESS": "0x123abc...",
    "FUNDRAISE_NFT_CONTRACT_ABI": [
        {
            "inputs": [
                {"type": "address", "name": "to"},
                {"type": "uint256", "name": "amount"},
                {"type": "uint256", "name": "fundraiseId"},
            ],
            "name": "mint",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        }
    ],
    "WEB3_WALLET_ADDRESS": "0x456def...",
    "WEB3_PRIVATE_KEY": "0x789ghi...",
    "WEB3_BASE_PROVIDER_URL": "http://localhost:8545",
}


@override_settings(**TEST_SETTINGS)
class FundraiseNFTTests(APITestCase):
    def setUp(self):
        self.user = create_random_authenticated_user("test_user")
        self.user.wallet_address = "0xabc123..."
        self.user.save()

        self.fundraise = Fundraise.objects.create(
            title="Test Fundraise",
            description="Test Description",
            goal_amount=1000,
            total_nfts=10,
            creator=self.user,
        )

        # Use the test provider from web3_provider
        self.w3 = web3_provider.base

    def test_mint_fundraise_nfts_success(self):
        """Test successful NFT minting"""
        result = mint_fundraise_nfts(
            user_id=self.user.id, fundraise_id=self.fundraise.id, amount=5
        )

        # Verify transaction hash returned
        self.assertTrue(isinstance(result, str))
        self.assertTrue(result.startswith("0x"))

    def test_mint_fundraise_nfts_failure(self):
        """Test NFT minting failure"""
        # Modify contract address to force failure
        with override_settings(
            FUNDRAISE_NFT_CONTRACT_ADDRESS="0x0000000000000000000000000000000000000000"
        ):
            with self.assertRaises(Exception):
                mint_fundraise_nfts(
                    user_id=self.user.id, fundraise_id=self.fundraise.id, amount=5
                )
