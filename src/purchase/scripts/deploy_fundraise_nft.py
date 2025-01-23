import json
import shutil
from pathlib import Path

from django.conf import settings
from web3.middleware import geth_poa_middleware

from utils.sentry import log_error
from utils.web3_utils import web3_provider


def setup_brownie_project():
    """Setup Brownie project structure"""
    project_path = Path(__file__).parent.parent / "brownie_project"

    # Create all required directories
    project_path.mkdir(exist_ok=True, parents=True)

    # Initialize brownie project structure
    build_path = project_path / "build"
    contracts_path = project_path / "contracts"
    interfaces_path = project_path / "interfaces"
    reports_path = project_path / "reports"
    scripts_path = project_path / "scripts"
    tests_path = project_path / "tests"

    for path in [
        build_path,
        contracts_path,
        interfaces_path,
        reports_path,
        scripts_path,
        tests_path,
    ]:
        path.mkdir(exist_ok=True, parents=True)

    # Create brownie-config.yaml
    config_content = """
compiler:
    solc:
        version: 0.8.20
        optimizer:
            enabled: true
            runs: 200
dependencies:
    - OpenZeppelin/openzeppelin-contracts@4.9.0
networks:
    default: development
    development:
        gas_limit: max
        gas_price: 0
    base-custom:
        gas_limit: max
        gas_price: auto
"""
    with open(project_path / "brownie-config.yaml", "w") as f:
        f.write(config_content)

    # Copy contract to Brownie project
    source = Path(__file__).parent.parent / "contracts" / "FundraiseNFT.sol"
    dest = contracts_path / "FundraiseNFT.sol"
    shutil.copy(source, dest)

    return project_path


def deploy_fundraise_nft():
    try:
        from brownie import accounts, network, project

        # Setup Brownie project
        project_path = setup_brownie_project()
        Project = project.load(project_path, name="FundraiseNFT")

        # Connect to Base network
        network.connect("base-custom", host=settings.WEB3_BASE_PROVIDER_URL)

        # Load account from private key
        deployer = accounts.add(settings.WEB3_PRIVATE_KEY)

        # Deploy contract
        contract = Project.FundraiseNFT.deploy({"from": deployer})

        # Save ABI
        abi_path = Path(__file__).parent.parent / "contracts" / "FundraiseNFT.json"
        with open(abi_path, "w") as file:
            json.dump(contract.abi, file, indent=2)

        print(f"Contract deployed to: {contract.address}")
        return contract.address

    except Exception as e:
        log_error(e, message="Failed to deploy FundraiseNFT contract")
        raise


if __name__ == "__main__":
    deploy_fundraise_nft()
