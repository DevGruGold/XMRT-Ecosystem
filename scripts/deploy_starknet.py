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

    contracts_to_deploy = [
        "xmrt",
        "ai_agent_interface",
        "autonomous_agent_registry",
        "autonomous_dao",
        "autonomous_dao_core",
        "autonomous_treasury",
        "dao_governance",
        "dao_treasury",
        "governance",
        "xmrt_cross_chain",
        "xmrt_layer_zero_oft",
        "vault",
        "agent_manager"
    ]

    deployed_contracts = {}

    for contract_name in contracts_to_deploy:
        print(f"Deploying {contract_name}.cairo...")
        with open(f"../contracts-cairo/{contract_name}.json", "r") as f:
            compiled_contract = f.read()

        # Declare the contract
        declare_result = await Contract.declare(account=account, compiled_contract=compiled_contract, max_fee=10**16)
        await declare_result.wait_for_acceptance()
        print(f"{contract_name} Contract declared at class hash: {declare_result.class_hash}")

        # Deploy the contract
        # Constructor arguments will need to be dynamically determined based on each contract
        # For now, assuming no constructor arguments or empty ones
        constructor_args = {}
        if contract_name == "xmrt":
            constructor_args = {"initial_supply": 10000000000000000000000000} # Example initial supply
        elif contract_name == "ai_agent_interface":
            # Placeholder for actual addresses once other contracts are deployed
            constructor_args = {"_dao_governance": 0, "_dao_treasury": 0, "_xmrt_token": 0}

        deploy_result = await declare_result.deploy(constructor_args=constructor_args, max_fee=10**16)
        await deploy_result.wait_for_acceptance()
        print(f"{contract_name} Contract deployed at address: {deploy_result.contract_address}")
        deployed_contracts[contract_name] = deploy_result.contract_address

    print("\nAll contracts deployed:")
    for name, address in deployed_contracts.items():
        print(f"{name}: {address}")

if __name__ == "__main__":
    asyncio.run(deploy())


