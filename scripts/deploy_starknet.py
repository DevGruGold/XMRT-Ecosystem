import asyncio
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.selector import get_selector_from_name

async def deploy():
    # Replace with your actual private key and address
    private_key = 0x123 # Replace with your private key
    account_address = 0x456 # Replace with your account address

    client = FullNodeClient(node_url="http://localhost:5050") # Or your Starknet node URL
    signer = StarkCurveSigner(account_address, private_key, StarknetChainId.TESTNET)
    account = Account(client=client, address=account_address, signer=signer)

    # Read compiled Cairo contract (replace with your actual .json path)
    with open("../contracts-cairo/xmrt.json", "r") as f:
        compiled_contract = f.read()

    # Declare and deploy the contract
    declare_result = await Contract.declare(account=account, compiled_contract=compiled_contract, max_fee=10**16)
    await declare_result.wait_for_acceptance()
    print(f"XMRT Contract declared at class hash: {declare_result.class_hash}")

    deploy_result = await declare_result.deploy(constructor_args={}, max_fee=10**16)
    await deploy_result.wait_for_acceptance()
    print(f"XMRT Contract deployed at address: {deploy_result.contract_address}")

if __name__ == "__main__":
    asyncio.run(deploy())


