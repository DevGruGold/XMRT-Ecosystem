/// @title AutonomousAgentRegistry
/// @notice This contract manages autonomous agents with execution authority in Cairo.

#[contract]
mod AutonomousAgentRegistry {
    use starknet::get_caller_address;
    use starknet::ContractAddress;
    use starknet::get_block_timestamp;
    use array::ArrayTrait;
    use traits::Into;

    // Roles (simplified for Cairo)
    const ADMIN_ROLE: felt252 = 'ADMIN_ROLE';
    const AGENT_ROLE: felt252 = 'AGENT_ROLE';
    const EXECUTOR_ROLE: felt252 = 'EXECUTOR_ROLE';

    struct Agent {
        id: u256,
        agent_address: ContractAddress,
        name: felt252,
        description: felt252,
        reputation: u256,
        execution_count: u256,
        is_active: bool,
        registration_time: u64,
        staking_amount: u256,
        agent_type: AgentType,
        permissions: Array<Permission>,
    }

    enum AgentType {
        GOVERNANCE,
        TREASURY,
        PROPOSAL_EXECUTOR,
        ORACLE,
        SECURITY,
        COMMUNITY,
    }

    enum Permission {
        EXECUTE_PROPOSALS,
        MANAGE_TREASURY,
        UPDATE_GOVERNANCE,
        ACCESS_ORACLES,
        EMERGENCY_ACTIONS,
        COMMUNITY_MANAGEMENT,
    }

    struct Storage {
        agent_id_counter: u256,
        agents: LegacyMap<u256, Agent>,
        agent_address_to_id: LegacyMap<ContractAddress, u256>,
        authorized_agents: LegacyMap<ContractAddress, bool>,
        minimum_staking: u256,
        total_active_agents: u256,
        admin_address: ContractAddress,
    }

    #[constructor]
    fn constructor() {
        Storage::write(minimum_staking, 1000 * 10_u256.pow(18)); // 1000 XMRT tokens
        Storage::write(admin_address, get_caller_address());
        Internal::grant_role(get_caller_address(), ADMIN_ROLE);
    }

    #[flat]
    fn register_agent(
        agent_address: ContractAddress,
        name: felt252,
        description: felt252,
        reputation: u256,
        staking_amount: u256,
        agent_type: AgentType,
        permissions: Array<Permission>,
    ) -> u256 {
        Internal::only_authorized_agent();
        assert(agent_address != 0.into(), 'Invalid agent address');
        assert(Storage::read(agent_address_to_id.read(agent_address)) == 0, 'Agent already registered');
        assert(staking_amount >= Storage::read(minimum_staking), 'Insufficient staking amount');

        let mut agent_id_counter = Storage::read(agent_id_counter);
        agent_id_counter += 1;
        Storage::write(agent_id_counter, agent_id_counter);
        let new_agent_id = agent_id_counter;

        let new_agent = Agent {
            id: new_agent_id,
            agent_address: agent_address,
            name: name,
            description: description,
            reputation: reputation,
            execution_count: 0,
            is_active: true,
            registration_time: get_block_timestamp(),
            staking_amount: staking_amount,
            agent_type: agent_type,
            permissions: permissions,
        };
        Storage::write(agents.write(new_agent_id, new_agent));
        Storage::write(agent_address_to_id.write(agent_address, new_agent_id));

        let total_active_agents = Storage::read(total_active_agents);
        Storage::write(total_active_agents, total_active_agents + 1);

        // Emit AgentRegistered event (simplified)
        // emit AgentRegistered(new_agent_id, agent_address, name, description, reputation, staking_amount, agent_type);

        new_agent_id
    }

    #[flat]
    fn activate_agent(agent_id: u256) {
        Internal::only_authorized_agent();
        let mut agent = Storage::read(agents.read(agent_id));
        assert(agent.id != 0, 'Agent not found');
        assert(!agent.is_active, 'Agent already active');

        agent.is_active = true;
        Storage::write(agents.write(agent_id, agent));

        let total_active_agents = Storage::read(total_active_agents);
        Storage::write(total_active_agents, total_active_agents + 1);

        // Emit AgentActivated event (simplified)
        // emit AgentActivated(agent_id, agent.agent_address);
    }

    #[flat]
    fn deactivate_agent(agent_id: u256) {
        Internal::only_authorized_agent();
        let mut agent = Storage::read(agents.read(agent_id));
        assert(agent.id != 0, 'Agent not found');
        assert(agent.is_active, 'Agent already inactive');

        agent.is_active = false;
        Storage::write(agents.write(agent_id, agent));

        let total_active_agents = Storage::read(total_active_agents);
        Storage::write(total_active_agents, total_active_agents - 1);

        // Emit AgentDeactivated event (simplified)
        // emit AgentDeactivated(agent_id, agent.agent_address);
    }

    #[flat]
    fn grant_permission(agent_id: u256, permission: Permission) {
        Internal::only_authorized_agent();
        let mut agent = Storage::read(agents.read(agent_id));
        assert(agent.id != 0, 'Agent not found');

        let mut found = false;
        let mut permissions_array = agent.permissions;
        let mut i = 0;
        loop {
            if i == permissions_array.len() {
                break;
            }
            if *permissions_array.at(i) == permission {
                found = true;
                break;
            }
            i += 1;
        };
        assert(!found, 'Permission already granted');

        permissions_array.append(permission);
        agent.permissions = permissions_array;
        Storage::write(agents.write(agent_id, agent));

        // Emit PermissionGranted event (simplified)
        // emit PermissionGranted(agent_id, permission);
    }

    #[flat]
    fn revoke_permission(agent_id: u256, permission: Permission) {
        Internal::only_authorized_agent();
        let mut agent = Storage::read(agents.read(agent_id));
        assert(agent.id != 0, 'Agent not found');

        let mut found = false;
        let mut permissions_array = agent.permissions;
        let mut i = 0;
        loop {
            if i == permissions_array.len() {
                break;
            }
            if *permissions_array.at(i) == permission {
                permissions_array.swap_remove(i);
                found = true;
                break;
            }
            i += 1;
        };
        assert(found, 'Permission not found');

        agent.permissions = permissions_array;
        Storage::write(agents.write(agent_id, agent));

        // Emit PermissionRevoked event (simplified)
        // emit PermissionRevoked(agent_id, permission);
    }

    #[flat]
    fn update_reputation(agent_id: u256, new_reputation: u256) {
        Internal::only_authorized_agent();
        let mut agent = Storage::read(agents.read(agent_id));
        assert(agent.id != 0, 'Agent not found');
        agent.reputation = new_reputation;
        Storage::write(agents.write(agent_id, agent));

        // Emit ReputationUpdated event (simplified)
        // emit ReputationUpdated(agent_id, new_reputation);
    }

    #[flat]
    fn execute_agent_action(agent_id: u256, target: ContractAddress, value: u256) {
        Internal::only_active_agent(agent_id);
        Internal::only_authorized_agent();
        assert(target != 0.into(), 'Invalid target address');

        let mut agent = Storage::read(agents.read(agent_id));
        agent.execution_count += 1;
        Storage::write(agents.write(agent_id, agent));

        // Simulate call to target contract (Cairo doesn't have direct call with data yet)
        // This would require a dispatcher for the target contract
        // For now, just emit an event
        // emit AgentExecuted(agent_id, target, data, value);
    }

    #[view]
    fn get_agent(
        agent_id: u256
    ) -> (
        u256,
        ContractAddress,
        felt252,
        felt252,
        u256,
        u256,
        bool,
        u64,
        u256,
        AgentType,
        Array<Permission>,
    ) {
        let agent = Storage::read(agents.read(agent_id));
        assert(agent.id != 0, 'Agent not found');
        (
            agent.id,
            agent.agent_address,
            agent.name,
            agent.description,
            agent.reputation,
            agent.execution_count,
            agent.is_active,
            agent.registration_time,
            agent.staking_amount,
            agent.agent_type,
            agent.permissions,
        )
    }

    #[view]
    fn get_agent_id_by_address(agent_address: ContractAddress) -> u256 {
        Storage::read(agent_address_to_id.read(agent_address))
    }

    #[view]
    fn is_authorized(agent_address: ContractAddress) -> bool {
        Storage::read(authorized_agents.read(agent_address))
    }

    #[view]
    fn get_total_active_agents() -> u256 {
        Storage::read(total_active_agents)
    }

    #[flat]
    fn set_minimum_staking(new_minimum_staking: u256) {
        Internal::only_admin();
        Storage::write(minimum_staking, new_minimum_staking);
    }

    #[flat]
    fn authorize_agent(agent_address: ContractAddress) {
        Internal::only_admin();
        assert(agent_address != 0.into(), 'Invalid address');
        assert(!Storage::read(authorized_agents.read(agent_address)), 'Agent already authorized');
        Storage::write(authorized_agents.write(agent_address, true));
    }

    #[flat]
    fn deauthorize_agent(agent_address: ContractAddress) {
        Internal::only_admin();
        assert(agent_address != 0.into(), 'Invalid address');
        assert(Storage::read(authorized_agents.read(agent_address)), 'Agent not authorized');
        Storage::write(authorized_agents.write(agent_address, false));
    }

    mod Internal {
        use starknet::get_caller_address;
        use starknet::ContractAddress;
        use super::Storage;
        use super::Agent;
        use super::ADMIN_ROLE;

        fn only_admin() {
            assert(get_caller_address() == Storage::read(admin_address), 'AutonomousAgentRegistry: Not admin');
        }

        fn only_active_agent(agent_id: u256) {
            let agent = Storage::read(agents.read(agent_id));
            assert(agent.is_active, 'Agent is not active');
        }

        fn only_authorized_agent() {
            assert(Storage::read(authorized_agents.read(get_caller_address())), 'Not an authorized agent');
        }

        fn grant_role(account: ContractAddress, role: felt252) {
            // In Cairo, roles are typically managed by checking against specific addresses or mappings.
            // For simplicity, we'll just authorize the agent directly if it's the admin role.
            if role == ADMIN_ROLE {
                Storage::write(authorized_agents.write(account, true));
            }
        }
    }
}


