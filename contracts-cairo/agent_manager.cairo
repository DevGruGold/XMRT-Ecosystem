/// @title AgentManager
/// @notice This contract manages agents and their roles in Cairo.

#[contract]
mod AgentManager {
    use starknet::get_caller_address;
    use starknet::ContractAddress;
    use starknet::get_block_timestamp;
    use array::ArrayTrait;
    use traits::Into;

    // Roles (simplified for Cairo)
    const ADMIN_ROLE: felt252 = 'ADMIN_ROLE';
    const AGENT_ROLE: felt252 = 'AGENT_ROLE';

    struct Storage {
        admin_address: ContractAddress,
        agent_roles: LegacyMap<(ContractAddress, felt252), bool>,
        // Add other storage variables as needed for agent management
    }

    #[constructor]
    fn constructor() {
        Storage::write(admin_address, get_caller_address());
        Internal::grant_role(get_caller_address(), ADMIN_ROLE);
    }

    #[flat]
    fn grant_role(account: ContractAddress, role: felt252) {
        Internal::only_admin();
        Storage::write(agent_roles.write((account, role), true));
    }

    #[flat]
    fn revoke_role(account: ContractAddress, role: felt252) {
        Internal::only_admin();
        Storage::write(agent_roles.write((account, role), false));
    }

    #[view]
    fn has_role(account: ContractAddress, role: felt252) -> bool {
        Storage::read(agent_roles.read((account, role)))
    }

    mod Internal {
        use starknet::get_caller_address;
        use starknet::ContractAddress;
        use super::Storage;
        use super::ADMIN_ROLE;

        fn only_admin() {
            assert(get_caller_address() == Storage::read(admin_address), 'AgentManager: Not admin');
        }
    }
}


